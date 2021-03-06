import numpy as np
import argparse
import utils.ir_models as ir_model
from utils.ir_model_helper import *


def run_split_model_1(gest_set, cv_strategy):
    model_fn = ir_model.split_model_1
    hyper_param_path = "./gridSearch/split_model_1/"
    model_result_path = "/split_model_1/Model"
    if cv_strategy == 'loso':
        loso_cv(model_fn, gest_set=gest_set, hyper_param_path=hyper_param_path,
                results_file_path="./leave_one_subject/ir" + model_result_path)
    elif cv_strategy == 'personalized':
        personalized_cv(model_fn, gest_set=gest_set, hyper_param_path=hyper_param_path,
                        results_file_path="./personalized_cv/ir" + model_result_path)
    elif cv_strategy == 'user_calibrated':
        train_size = 0.6
        user_split_cv(model_fn, gest_set=gest_set, hyper_param_path=hyper_param_path, train_size=train_size,
                      results_file_path="./user_split_cv/doppler" + model_result_path)
    else:
        raise ValueError("Cross-validation strategy not defined")


def run_split_model_2(gest_set, cv_strategy):
    model_fn = ir_model.split_model_2
    hyper_param_path = "./gridSearch/split_model_2/"
    model_result_path = "/split_model_2/Model"
    if cv_strategy == 'loso':
        loso_cv(model_fn, gest_set=gest_set, hyper_param_path=hyper_param_path,
                results_file_path="./leave_one_subject/ir" + model_result_path)
    elif cv_strategy == 'personalized':
        personalized_cv(model_fn, gest_set=gest_set, hyper_param_path=hyper_param_path,
                        results_file_path="./personalized_cv/ir" + model_result_path)
    elif cv_strategy == 'user_calibrated':
        train_size = 0.6
        user_split_cv(model_fn, gest_set=gest_set, hyper_param_path=hyper_param_path, train_size=train_size,
                      results_file_path="./user_split_cv/doppler" + model_result_path)
    else:
        raise ValueError("Cross-validation strategy not defined")

def run_split_model_3(gest_set, cv_strategy):
    model_fn = ir_model.split_model_3
    hyper_param_path = "./gridSearch/split_model_3/"
    model_result_path = "/split_model_3/Model"
    if cv_strategy == 'loso':
        loso_cv(model_fn, gest_set=gest_set, hyper_param_path=hyper_param_path,
                results_file_path="./leave_one_subject/ir" + model_result_path)
    elif cv_strategy == 'personalized':
        personalized_cv(model_fn, gest_set=gest_set, hyper_param_path=hyper_param_path,
                        results_file_path="./personalized_cv/ir" + model_result_path)
    elif cv_strategy == 'user_calibrated':
        train_size = 0.6
        user_split_cv(model_fn, gest_set=gest_set, hyper_param_path=hyper_param_path, train_size=train_size,
                      results_file_path="./user_split_cv/doppler" + model_result_path)
    else:
        raise ValueError("Cross-validation strategy not defined")


def run_split_model_4(gest_set, cv_strategy):
    model_fn = ir_model.split_model_4
    hyper_param_path = "./gridSearch/split_model_4/"
    model_result_path = "/split_model_4/Model"
    if cv_strategy == 'loso':
        loso_cv(model_fn, gest_set=gest_set, hyper_param_path=hyper_param_path,
                results_file_path="./leave_one_subject/ir" + model_result_path)
    elif cv_strategy == 'personalized':
        personalized_cv(model_fn, gest_set=gest_set, hyper_param_path=hyper_param_path,
                        results_file_path="./personalized_cv/ir" + model_result_path)
    elif cv_strategy == 'user_calibrated':
        train_size = 0.6
        user_split_cv(model_fn, gest_set=gest_set, hyper_param_path=hyper_param_path, train_size=train_size,
                      results_file_path="./user_split_cv/doppler" + model_result_path)
    else:
        raise ValueError("Cross-validation strategy not defined")


if __name__ == '__main__':
    model_map = {'model_1': run_split_model_1,
                 'model_2': run_split_model_2,
                 'model_3': run_split_model_3,
                 'model_4': run_split_model_4}
    parser = argparse.ArgumentParser(description="AirWare grid search and train model using different CV strategies")
    # "?" one argument consumed from the command line and produced as a single item
    # Positional arguments
    parser.add_argument('-model',
                        help="Define model architecture",
                        choices=['model_1', 'model_2', 'model_3', 'model_4'])

    parser.add_argument('-cv_strategy',
                        help="Define CV Strategy. loso: Leave one subject out, user_calibrated: Partial train and test "
                             "user, personalized_cv: Train and test only for a given user",
                        choices=['loso', 'user_calibrated',
                                 'personalized'])
    parser.add_argument('-gesture_set', type=int, default=1,
                        help="Gesture set. 1: All gestures, 2: Reduced Gesture 1, 3: Reduced Gesture 2, 4: Reduced "
                             "Gesture 3, 5: Reduced Gesture 4. Default is full gesture set",
                        choices=range(1, 6))
    args = parser.parse_args()
    run_model = model_map[args.model]

    print("Cross Validation Strategy: ", args.cv_strategy, " for model: ", args.model)
    run_model(gest_set=args.gesture_set, cv_strategy=args.cv_strategy)