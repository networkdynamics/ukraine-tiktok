import os

import numpy as np
import pandas as pd
import sklearn
from sklearn import metrics
import transformers
import torch
import torch.nn.functional as F

import evaluate

class DescDataset(torch.utils.data.Dataset):
    def __init__(self, df, model_name):
        self.df = df
        self.tokenizer = transformers.AutoTokenizer.from_pretrained(model_name)

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        text = row['desc']
        label = row['class']

        encoding = self.tokenizer(text, return_tensors='pt', padding='max_length', truncation=True, max_length=512)
        return {
            'input_ids': encoding['input_ids'][0], 
            'attention_mask': encoding['attention_mask'][0], 
            'label': torch.tensor(label)
        }

class ImbalancedTrainer(transformers.Trainer):
    def __init__(self, *args, class_weights=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_weights = class_weights

    def compute_loss(self, model, inputs, return_outputs=False):
        labels = inputs.get("labels")
        # forward pass
        outputs = model(**inputs)
        logits = outputs.get("logits")
        # compute custom loss (suppose one has 3 labels with different weights)
        loss_fct = torch.nn.CrossEntropyLoss(weight=self.class_weights)
        loss = loss_fct(logits.view(-1, self.model.config.num_labels), labels.view(-1))
        return (loss, outputs) if return_outputs else loss

class RelatedClassifier:
    def __init__(self, model_name, train_dataset, eval_dataset):
        this_dir_path = os.path.dirname(os.path.abspath(__file__))
        data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')
        classifier_dir_path = os.path.join(data_dir_path, 'outputs', 'related_classifier')
        if not os.path.exists(classifier_dir_path):
            os.mkdir(classifier_dir_path)

        # compute class weights
        weights = sklearn.utils.class_weight.compute_class_weight('balanced', np.unique(train_dataset.df['class']), train_dataset.df['class'].values)
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        weights = torch.tensor(weights, dtype=torch.float32, device=device)

        self.model = transformers.AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
        self.training_args = transformers.TrainingArguments(
            output_dir=classifier_dir_path, 
            evaluation_strategy="epoch",
            num_train_epochs=30,
            load_best_model_at_end=True,
            save_strategy="epoch",
            save_total_limit=1,
            metric_for_best_model='eval_accuracy'
        )
        self.metric = evaluate.load("accuracy")
        self.trainer = ImbalancedTrainer(
            model=self.model,
            args=self.training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            compute_metrics=self.compute_metrics,
            class_weights=weights
        )

    def train(self):
        self.trainer.train()

    def evaluate(self):
        return self.trainer.evaluate()

    def compute_metrics(self, eval_pred):
        logits, labels = eval_pred
        predictions = np.argmax(logits, axis=-1)
        return self.metric.compute(predictions=predictions, references=labels)

def main():
    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')

    dfs = []
    for filename in os.listdir(os.path.join(data_dir_path, 'outputs')):
        if filename.startswith('desc_') and filename.endswith('.csv'):
            df = pd.read_csv(os.path.join(data_dir_path, 'outputs', filename))
            dfs.append(df)

    related_df = pd.concat(dfs)

    related_df = related_df[related_df['related'].notna()]
    related_df['class'] = related_df['related'].apply(lambda x: 1 if x == 'Y' else 0)

    video_df = pd.read_csv(os.path.join(data_dir_path, 'cache', 'all_videos.csv'))
    related_df = related_df.merge(video_df[['video_id', 'desc']], on='video_id')
    related_df = related_df[related_df['desc'].notna()]

    # shuffle the dataset
    related_df = related_df.sample(frac=1).reset_index(drop=True)

    split = 0.7
    train_df = related_df.iloc[:int(len(related_df) * split)]
    test_df = related_df.iloc[int(len(related_df) * split):]

    model_name = 'roberta-base'

    train_dataset = DescDataset(train_df, model_name)
    test_dataset = DescDataset(test_df, model_name)

    classifier = RelatedClassifier(model_name, train_dataset, test_dataset)

    train = True
    if train:
        classifier.train()

    test = True
    if test:
        print(classifier.evaluate())

    output = classifier.trainer.predict(test_dataset)
    prediction = F.softmax(torch.tensor(output.predictions), dim=1)
    y_pred = torch.argmax(prediction, dim=1).numpy()
    confusion_matrix = metrics.confusion_matrix(output.label_ids, y_pred)
    print(confusion_matrix)

    classifier.trainer.save_model()

if __name__ == '__main__':
    main()