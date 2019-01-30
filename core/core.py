import json
import os

from core.binary_classification import binary_classifier, binary_classifier_single_log
from core.constants import \
    CLASSIFICATION, REGRESSION, LABELLING
from core.label_validation import label_task
from core.multi_classification import multi_classifier, multi_classifier_single_log
from core.regression import regression, regression_single_log
from encoders.common import encode_label_logs, REMAINING_TIME, ATTRIBUTE_NUMBER, ATTRIBUTE_STRING, NEXT_ACTIVITY, \
    encode_label_log, DURATION
from log_util.cache import load_from_cache, dump_to_cache, get_digested
from logs.splitting import prepare_logs


def calculate(job):
    """ Main entry method for calculations"""
    print("Start job {} with {}".format(job['type'], get_run(job)))

    training_df, test_df = get_encoded_logs(job)
    results, model_split = run_by_type(training_df, test_df, job)
    return results, model_split


def get_encoded_logs(job: dict):
    processed_df_cache = ('split-%s_encoding-%s_type-%s_label-%s' % (json.dumps(job['split']),
                                                                            json.dumps(job['encoding']),
                                                                            json.dumps(job['type']),
                                                                            json.dumps(job['label'])))

    if os.path.isfile("labeled_log_cache/" + get_digested(processed_df_cache) + '.pickle'):

        print('Found Labeled Dataset in cache, loading...')
        training_df, test_df = load_from_cache(processed_df_cache, prefix="labeled_log_cache/")
        print('Done.')

    else:
        df_cache = ('split-%s' % (json.dumps(job['split'])))

        if os.path.isfile("labeled_log_cache/" + get_digested(df_cache) + '.pickle'):

            print('Found Dataset in cache, loading..')
            training_log, test_log, additional_columns = load_from_cache(df_cache, prefix="labeled_log_cache/")
            print('Dataset loaded.')

        else:
            training_log, test_log, additional_columns = prepare_logs(job['split'])

            dump_to_cache(df_cache, (training_log, test_log, additional_columns), prefix="labeled_log_cache/")

        training_df, test_df = encode_label_logs(training_log, test_log, job['encoding'], job['type'], job['label'],
                                                 additional_columns=additional_columns)

        dump_to_cache(processed_df_cache, (training_df, test_df), prefix="labeled_log_cache/")

    return training_df, test_df


def run_by_type(training_df, test_df, job):
    model_split = None
    if job['type'] == CLASSIFICATION:
        label_type = job['label'].type
        # Binary classification
        if label_type == REMAINING_TIME or label_type == ATTRIBUTE_NUMBER or label_type == DURATION:
            results, model_split = binary_classifier(training_df, test_df, job)
        elif label_type == NEXT_ACTIVITY or label_type == ATTRIBUTE_STRING:
            results, model_split = multi_classifier(training_df, test_df, job)
        else:
            raise ValueError("Label type not supported", label_type)
    elif job['type'] == REGRESSION:
        results, model_split = regression(training_df, test_df, job)
    elif job['type'] == LABELLING:
        results = label_task(training_df)
    else:
        raise ValueError("Type not supported", job['type'])
    print("End job {}, {} . Results {}".format(job['type'], get_run(job), results))
    return results, model_split


def runtime_calculate(run_log, model):
    run_df = encode_label_log(run_log, model['encoding'], model['type'], model['label'])
    if model['type'] == CLASSIFICATION:
        label_type = model['label'].type
        if label_type == REMAINING_TIME or label_type == ATTRIBUTE_NUMBER or label_type == DURATION:
            results = binary_classifier_single_log(run_df, model)
        elif label_type == NEXT_ACTIVITY or label_type == ATTRIBUTE_STRING:
            results = multi_classifier_single_log(run_df, model)
        else:
            raise ValueError("Label type not supported", label_type)
    elif model['type'] == REGRESSION:
        results = regression_single_log(run_df, model)
    else:
        raise ValueError("Type not supported", model['type'])
    print("End job {}, {} . Results {}".format(model['type'], get_run(model), results))
    return results


def get_run(job):
    """Defines job identity"""
    if job['type'] == LABELLING:
        return job['encoding'].method + '_' + job['label'].type
    return job['method'] + '_' + job['encoding'].method + '_' + job['clustering'] + '_' + job['label'].type
