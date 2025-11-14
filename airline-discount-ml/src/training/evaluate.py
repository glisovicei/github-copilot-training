def evaluate_model(model, test_data):
    predictions = model.predict(test_data)
    accuracy = calculate_accuracy(predictions, test_data.labels)
    return {
        'predictions': predictions,
        'accuracy': accuracy
    }

def calculate_accuracy(predictions, labels):
    correct_predictions = sum(p == l for p, l in zip(predictions, labels))
    return correct_predictions / len(labels) if labels else 0.0