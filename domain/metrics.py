class Evaluator:
    @staticmethod
    def calculate_metrics(true_labels, predicted_labels):
        tp = sum(1 for t, p in zip(true_labels, predicted_labels) if t == 1 and p == 1)
        tn = sum(1 for t, p in zip(true_labels, predicted_labels) if t == 0 and p == 0)
        fp = sum(1 for t, p in zip(true_labels, predicted_labels) if t == 0 and p == 1)
        fn = sum(1 for t, p in zip(true_labels, predicted_labels) if t == 1 and p == 0)
        
        accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "falsos_positivos": fp,
            "falsos_negativos": fn
        }
