from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator
from itertools import chain

def evaluate_model(model, test_data, prefix=""):
    print("Evaluating the model ...")
    pred_pipeline = model.transform(test_data)

    evaluator = BinaryClassificationEvaluator()
    roc = evaluator.evaluate(pred_pipeline)

    evaluator = MulticlassClassificationEvaluator()
    return {
               prefix + "accuracy": evaluator.evaluate(pred_pipeline, {evaluator.metricName: "accuracy"}),
               prefix + "f1": evaluator.evaluate(pred_pipeline),
               prefix + "weightedPrecision": evaluator.evaluate(pred_pipeline,
                                                                {evaluator.metricName: "weightedPrecision"}),
               prefix + "weightedRecall": evaluator.evaluate(pred_pipeline, {evaluator.metricName: "weightedRecall"}),
               prefix + "AU-ROC": roc
           }, pred_pipeline


def calculate_confusion_matrix(predictions):
    return predictions.select(['prediction', 'label']).groupby("label").pivot(
        "prediction").count().drop("label").toPandas() / predictions.count()


def calculate_feature_importance(predictions, coefficients, features_col="features"):
    attrs = sorted(
        (attr["idx"], attr["name"]) for attr in (chain(*predictions
                                                       .schema[features_col]
                                                       .metadata["ml_attr"]["attrs"].values())))

    return {name: coefficients[idx] for idx, name in attrs}
