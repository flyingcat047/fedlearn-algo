import setup
setup.deal_with_path()

import numpy as np
import linreg_qr
import linreg_setup
import math


def demo_local_generated_data(nFeatures, qrMthd="GramSchmidt"):
    print("*"*80)
    print("Demonstrate the performance of federated QR with remote clients implemented by ", qrMthd, " method")
    dataMax = 10**4
    print("The features are generated with variate scales. The largest scale is ", dataMax)
    print("The label values are generated by adding the multiplication of the features and some random generated weights with some perturbation")
    clientIdWLabel = 1
    print("The label is kept by beh second client")
    colPivot = False

    print("="*60)
    print("Problem1: Performance on small scale problem")
    nTraining = 1000
    nInference = 10
    print("The training data are generated randomly and consist of ", nTraining, " samples and ", sum(nFeatures), " features")
    print("The inference data are generated randomly and consist of ", nInference, " samples and ", sum(nFeatures), " features")
    encryLv = 3

    # Generate the training and inference data.
    XTrain, YTrain, XInfer = linreg_setup.generate_fullrank_test_data(nTraining, nInference, nFeatures, dataMax)
    client_map, coordinator = linreg_setup.setup_problem(XTrain, YTrain, nFeatures, clientIdWLabel, encryLv, XInfer, qrMthd, colPivot)

    # Start training process.
    print("Training Started.")
    phase = "0"
    init_requests = coordinator.init_training_control()
    responses = {}
    for client_info, reqi in init_requests.items():
        client = client_map[client_info]
        responses[client_info] = client.control_flow_client(reqi.phase_id, reqi)
    while True:
        phase = coordinator.get_next_phase(phase)
        print("Phase %s start..."%phase)
        requests = coordinator.control_flow_coordinator(phase, responses)
        responses = {}
        if coordinator.is_training_continue():
            for client_info, reqi in requests.items():
                client = client_map[client_info]
                responses[client_info] = client.control_flow_client(reqi.phase_id, reqi.copy())
        else:
            break
    print("Training finished.")
    weights = linreg_qr.obtain_global_weights(client_map, coordinator.machine_info_client)

    # Start inference process.
    print("Inference Started.")
    phase = "-1"
    init_requests = coordinator.init_inference_control()
    responses = {}
    for client_info, reqi in init_requests.items():
        client = client_map[client_info]
        responses[client_info] = client.control_flow_client(reqi.phase_id, reqi)
    while True:
        phase = coordinator.get_next_phase(phase)
        #logging.info("Phase %s start..."%phase)
        print("Phase %s start..."%phase)
        requests = coordinator.control_flow_coordinator(phase, responses)
        responses = {}
        if coordinator.is_inference_continue():
            for client_info, reqi in requests.items():
                client = client_map[client_info]
                responses[client_info] = client.control_flow_client(reqi.phase_id, reqi.copy())
        else:
            break
    prediction = coordinator.post_inference_session()
    print("Prediction: \n", prediction)

    # Do comparison.
    XTrain, XInfer = linreg_setup.switch_order_4_dataset(XTrain, nFeatures, clientIdWLabel, XInfer)
    XTrain = np.append(XTrain, np.ones([XTrain.shape[0], 1]), axis=1)
    weightsExact = np.linalg.lstsq(XTrain, YTrain, rcond=None)[0]
    err = weights-weightsExact
    print("The relative error of QR with ", qrMthd, " method based on inf-norm is: ", np.linalg.norm(err, np.inf)/np.linalg.norm(weightsExact, np.inf))
    print("The relative error of QR with ", qrMthd, " method based on 2-norm is: ", np.linalg.norm(err)/np.linalg.norm(weightsExact))
    XInfer = np.append(XInfer, np.ones([XInfer.shape[0], 1]), axis=1)
    predictionExact = np.matmul(XInfer, weightsExact)
    err = prediction-predictionExact
    print("The relative error of prediction based on inf-norm is: ", np.linalg.norm(err, np.inf)/np.linalg.norm(weightsExact, np.inf))
    print("The relative error of prediction based on 2-norm is: ", np.linalg.norm(err)/np.linalg.norm(weightsExact))

def demo_local_prestored_data(qrMthd="GramSchmidt"):
    print("*"*80)
    print("Demonstrate the performance of federated QR with remote clients implemented by ", qrMthd, " method")
    print("The features are the prestored data.")
    print("The label is kept by the first client")

    print("="*60)
    print("Problem1: Performance on classification data")
    encryLv = 3
    colTrunc = True

    # Generate the training and inference data.
    client_map, coordinator, XTrain, YTrain, XInfer = linreg_setup.setup_problem_4_prestored_data(encryLv, qrMthd, colTrunc)
    nTrain = XTrain.shape[0]
    nInfer = XInfer.shape[0]

    # Start training process.
    print("Training Started.")
    phase = "0"
    init_requests = coordinator.init_training_control()
    responses = {}
    for client_info, reqi in init_requests.items():
        client = client_map[client_info]
        responses[client_info] = client.control_flow_client(reqi.phase_id, reqi)
    while True:
        phase = coordinator.get_next_phase(phase)
        print("Phase %s start..."%phase)
        requests = coordinator.control_flow_coordinator(phase, responses)
        responses = {}
        if coordinator.is_training_continue():
            for client_info, reqi in requests.items():
                client = client_map[client_info]
                responses[client_info] = client.control_flow_client(reqi.phase_id, reqi.copy())
        else:
            break
    print("Training finished.")
    weights = linreg_qr.obtain_global_weights(client_map, coordinator.machine_info_client)

    # Start inference process.
    print("Inference Started.")
    phase = "-1"
    init_requests = coordinator.init_inference_control()
    responses = {}
    for client_info, reqi in init_requests.items():
        client = client_map[client_info]
        responses[client_info] = client.control_flow_client(reqi.phase_id, reqi)
    while True:
        phase = coordinator.get_next_phase(phase)
        #logging.info("Phase %s start..."%phase)
        print("Phase %s start..."%phase)
        requests = coordinator.control_flow_coordinator(phase, responses)
        responses = {}
        if coordinator.is_inference_continue():
            for client_info, reqi in requests.items():
                client = client_map[client_info]
                responses[client_info] = client.control_flow_client(reqi.phase_id, reqi.copy())
        else:
            break
    prediction = coordinator.post_inference_session()
    print("Prediction: \n", prediction)

    # Do comparison.
    nFeatures = [2, 2, 4]
    clientIdWLabel = 0
    XTrain, XInfer = linreg_setup.switch_order_4_dataset(XTrain, nFeatures, clientIdWLabel, XInfer)
    XTrain = np.append(XTrain, np.ones([XTrain.shape[0], 1]), axis=1)
    rmse = np.linalg.norm(np.matmul(XTrain, weights)-YTrain)/math.sqrt(nTrain)
    weightsExact = np.linalg.lstsq(XTrain, YTrain, rcond=None)[0]
    rmseExact = np.linalg.norm(np.matmul(XTrain, weightsExact)-YTrain)/math.sqrt(nTrain)
    diff = weights-weightsExact
    print("The root mean square error of federated QR with ", qrMthd, " method based on is: ", rmse)
    print("The root mean square error of numpy least square is: ", rmseExact)
    print("The relative difference of QR with ", qrMthd, " method against numpy least square based on inf-norm is: ", np.linalg.norm(diff, np.inf)/np.linalg.norm(weightsExact, np.inf))
    print("The relative difference of QR with ", qrMthd, " method against numpy least square based on 2-norm is: ", np.linalg.norm(diff)/np.linalg.norm(weightsExact))
    XInfer = np.append(XInfer, np.ones([XInfer.shape[0], 1]), axis=1)
    predictionExact = np.matmul(XInfer, weightsExact)
    diff = prediction-predictionExact
    print("The relative difference of prediction based on inf-norm is: ", np.linalg.norm(diff, np.inf)/np.linalg.norm(weightsExact, np.inf))
    print("The relative difference of prediction based on 2-norm is: ", np.linalg.norm(diff)/np.linalg.norm(weightsExact))

if __name__ == "__main__":
    nFeatures1 = [3, 3, 5, 11, 8]
    nFeatures2 = [4, 1, 15, 2, 8]
    nFeatures3 = [2, 0, 15, 11, 2]
    demo_local_generated_data(nFeatures1, "HouseHolder")
    demo_local_generated_data(nFeatures2, "HouseHolder")
    demo_local_generated_data(nFeatures3, "HouseHolder")
    demo_local_prestored_data(qrMthd="HouseHolder")
    demo_local_generated_data(nFeatures1, "GramSchmidt")
    demo_local_generated_data(nFeatures2, "GramSchmidt")
    demo_local_generated_data(nFeatures3, "GramSchmidt")
    demo_local_prestored_data(qrMthd="GramSchmidt")