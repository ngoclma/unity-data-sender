import pickle 
import sys

sys.path.append(r'/Users/AnhNgoc/Downloads/continuous_motor_trajectory_reconstruction_pipeline-main')

with open('trained_estimator_subject9a_session0.pkl', 'rb') as f:
    pipeline = pickle.load(f)
pipeline.steps[2][1].save_params('model_params_calibration9_epoch50.pkl')
