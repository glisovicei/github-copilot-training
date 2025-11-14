def train_model(model, data):
    """
    Train the machine learning model with the provided data.

    Parameters:
    model: The machine learning model to be trained.
    data: The training data used for training the model.

    Returns:
    The trained model.
    """
    model.fit(data['features'], data['labels'])
    return model