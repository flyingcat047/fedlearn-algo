import setup
setup.deal_with_path()

import numpy as np
import math
import linreg_qr
import linreg_setup


def test_accuracy(qrMthd="HouseHolder", colTrunc=False):
    print("*"*120)
    if colTrunc:
        print("Test the accuracy of federated QR implemented by ", qrMthd, " method with column pivoting")
    else:
        print("Test the accuracy of federated QR implemented by ", qrMthd, " method without column pivoting")
    nTrain = 1000
    nInfer = 10
    dataMax = 10**4
    print("The test data are generated randomly and consist of ", nTrain, " samples")
    print("The features are generated with variate scales. The largest scale is ", dataMax)
    print("The label values are generated by adding the multiplication of the features and some random generated weights with some perturbation")
    clientIdWLabel = 1
    print("The label is kept by beh second client")

    print("="*60)
    print("Problem1: Need not to add extra random features and the test features are full rank")
    nFeatures = [3, 3, 5, 11, 8]
    encryLv = 3
    XTrain, YTrain, XInfer = linreg_setup.generate_fullrank_test_data(nTrain, nInfer, nFeatures, dataMax)
    clientMap, coordinator= linreg_setup.setup_problem(XTrain, YTrain, nFeatures, clientIdWLabel, encryLv, XInfer, qrMthd, colTrunc)
    # XTrain, XInfer = linreg_setup.switch_order_4_dataset(XTrain, nFeatures, clientIdWLabel, XInfer)
    weights = linreg_qr.solve_weights(clientMap, coordinator, encryLv, qrMthd, colTrunc)
    XTrain = np.append(XTrain, np.ones([nTrain, 1]), axis=1)
    weightsExact = np.linalg.lstsq(XTrain, YTrain, rcond=None)[0]
    err = weights-weightsExact
    print("The relative error of QR with ", qrMthd, " method based on inf-norm is: ", np.linalg.norm(err, np.inf)/np.linalg.norm(weightsExact, np.inf))
    print("The relative error of QR with ", qrMthd, " method based on 2-norm is: ", np.linalg.norm(err)/np.linalg.norm(weightsExact))

    print("="*60)
    print("Problem2: Need to add extra random features and the test features are full rank")
    nFeatures = [4, 1, 15, 2, 8]
    encryLv = 3
    XTrain, YTrain, XInfer = linreg_setup.generate_fullrank_test_data(nTrain, nInfer, nFeatures, dataMax)
    clientMap, coordinator= linreg_setup.setup_problem(XTrain, YTrain, nFeatures, clientIdWLabel, encryLv, XInfer, qrMthd, colTrunc)
    # XTrain, XInfer = linreg_setup.switch_order_4_dataset(XTrain, nFeatures, clientIdWLabel, XInfer)
    weights = linreg_qr.solve_weights(clientMap, coordinator, encryLv, qrMthd, colTrunc)
    XTrain = np.append(XTrain, np.ones([nTrain, 1]), axis=1)
    weightsExact = np.linalg.lstsq(XTrain, YTrain, rcond=None)[0]
    err = weights-weightsExact
    print("The relative error of QR with ", qrMthd, " method based on inf-norm is: ", np.linalg.norm(err, np.inf)/np.linalg.norm(weightsExact, np.inf))
    print("The relative error of QR with ", qrMthd, " method based on 2-norm is: ", np.linalg.norm(err)/np.linalg.norm(weightsExact))

    print("="*60)
    print("Problem3: Need to add extra random features and the active client does not offer any feature. The test features are full rank")
    nFeatures = [2, 0, 15, 11, 2]
    encryLv = 3
    XTrain, YTrain, XInfer = linreg_setup.generate_fullrank_test_data(nTrain, nInfer, nFeatures, dataMax)
    clientMap, coordinator= linreg_setup.setup_problem(XTrain, YTrain, nFeatures, clientIdWLabel, encryLv, XInfer, qrMthd, colTrunc)
    # XTrain, XInfer = linreg_setup.switch_order_4_dataset(XTrain, nFeatures, clientIdWLabel, XInfer)
    weights = linreg_qr.solve_weights(clientMap, coordinator, encryLv, qrMthd, colTrunc)
    XTrain = np.append(XTrain, np.ones([nTrain, 1]), axis=1)
    weightsExact = np.linalg.lstsq(XTrain, YTrain, rcond=None)[0]
    err = weights-weightsExact
    print("The relative error of QR with ", qrMthd, " method based on inf-norm is: ", np.linalg.norm(err, np.inf)/np.linalg.norm(weightsExact, np.inf))
    print("The relative error of QR with ", qrMthd, " method based on 2-norm is: ", np.linalg.norm(err)/np.linalg.norm(weightsExact))

    if colTrunc:
        print("="*60)
        print("Problem4: Need not to add extra random features and the test features have rank deficient columns at both active and negative client.")
        nFeatures = [3, 3, 5, 11, 8]
        rankDefiColIds = [4, 11]
        encryLv = 3
        XTrain, YTrain, XInfer = linreg_setup.generate_rankdefi_test_data(nTrain, nInfer, nFeatures, dataMax, rankDefiColIds)
        clientMap, coordinator= linreg_setup.setup_problem(XTrain, YTrain, nFeatures, clientIdWLabel, encryLv, XInfer, qrMthd, colTrunc)
        # XTrain, XInfer = linreg_setup.switch_order_4_dataset(XTrain, nFeatures, clientIdWLabel, XInfer)
        weights = linreg_qr.solve_weights(clientMap, coordinator, encryLv, qrMthd, colTrunc)
        XTrain = np.append(XTrain, np.ones([nTrain, 1]), axis=1)
        rmse = np.linalg.norm(np.matmul(XTrain, weights)-YTrain)/math.sqrt(nTrain)
        weightsExact = np.linalg.lstsq(XTrain, YTrain, rcond=None)[0]
        rmseExact = np.linalg.norm(np.matmul(XTrain, weightsExact)-YTrain)/math.sqrt(nTrain)
        print("The root mean square error of federated QR with ", qrMthd, " method based on is: ", rmse)
        print("The root mean square error of numpy least square is: ", rmseExact)
        XInfer = np.append(XInfer, np.ones([nInfer, 1]), axis=1)
        prediction = np.matmul(XInfer, weights)
        predictionExact = np.matmul(XInfer, weightsExact)
        diff = prediction-predictionExact
        print("The relative difference of prediction based on inf-norm is: ", np.linalg.norm(diff, np.inf)/np.linalg.norm(predictionExact, np.inf))
        print("The relative difference of prediction based on 2-norm is: ", np.linalg.norm(diff)/np.linalg.norm(predictionExact))

        print("="*60)
        print("Problem5: Need to add extra random features and one of the client offers the test features which are all have rank deficient columns.")
        nFeatures = [3, 1, 3, 11, 12]
        rankDefiColIds = [3, 4, 5, 6]
        encryLv = 3
        XTrain, YTrain, XInfer = linreg_setup.generate_rankdefi_test_data(nTrain, nInfer, nFeatures, dataMax, rankDefiColIds)
        clientMap, coordinator= linreg_setup.setup_problem(XTrain, YTrain, nFeatures, clientIdWLabel, encryLv, XInfer, qrMthd, colTrunc)
        # XTrain, XInfer = linreg_setup.switch_order_4_dataset(XTrain, nFeatures, clientIdWLabel, XInfer)
        weights = linreg_qr.solve_weights(clientMap, coordinator, encryLv, qrMthd, colTrunc)
        XTrain = np.append(XTrain, np.ones([nTrain, 1]), axis=1)
        rmse = np.linalg.norm(np.matmul(XTrain, weights)-YTrain)/math.sqrt(nTrain)
        weightsExact = np.linalg.lstsq(XTrain, YTrain, rcond=None)[0]
        rmseExact = np.linalg.norm(np.matmul(XTrain, weightsExact)-YTrain)/math.sqrt(nTrain)
        print("The root mean square error of federated QR with ", qrMthd, " method based on is: ", rmse)
        print("The root mean square error of numpy least square is: ", rmseExact)
        XInfer = np.append(XInfer, np.ones([nInfer, 1]), axis=1)
        prediction = np.matmul(XInfer, weights)
        predictionExact = np.matmul(XInfer, weightsExact)
        diff = prediction-predictionExact
        print("The relative difference of prediction based on inf-norm is: ", np.linalg.norm(diff, np.inf)/np.linalg.norm(predictionExact, np.inf))
        print("The relative difference of prediction based on 2-norm is: ", np.linalg.norm(diff)/np.linalg.norm(predictionExact))

        print("="*60)
        print("Problem6: Use the prestored classification data as the training and inference data which is rank definicient.")
        encryLv = 3
        clientMap, coordinator, XTrain, YTrain, XInfer = linreg_setup.setup_problem_4_prestored_data(encryLv, qrMthd, colTrunc)
        # XTrain, XInfer = linreg_setup.switch_order_4_dataset(XTrain, nFeatures, clientIdWLabel, XInfer)
        nTrain = XTrain.shape[0]
        nInfer = XInfer.shape[0]
        weights = linreg_qr.solve_weights(clientMap, coordinator, encryLv, qrMthd, colTrunc)
        XTrain = np.append(XTrain, np.ones([nTrain, 1]), axis=1)
        rmse = np.linalg.norm(np.matmul(XTrain, weights)-YTrain)/math.sqrt(nTrain)
        weightsExact = np.linalg.lstsq(XTrain, YTrain, rcond=None)[0]
        rmseExact = np.linalg.norm(np.matmul(XTrain, weightsExact)-YTrain)/math.sqrt(nTrain)
        print("The root mean square error of federated QR with ", qrMthd, " method based on is: ", rmse)
        print("The root mean square error of numpy least square is: ", rmseExact)
        XInfer = np.append(XInfer, np.ones([nInfer, 1]), axis=1)
        prediction = np.matmul(XInfer, weights)
        predictionExact = np.matmul(XInfer, weightsExact)
        diff = prediction-predictionExact
        print("The relative difference of prediction based on inf-norm is: ", np.linalg.norm(diff, np.inf)/np.linalg.norm(predictionExact, np.inf))
        print("The relative difference of prediction based on 2-norm is: ", np.linalg.norm(diff)/np.linalg.norm(predictionExact))


# Start all the test for accuracy.
if __name__ == "__main__":
    test_accuracy("HouseHolder", False)
    test_accuracy("GramSchmidt", False)
    test_accuracy("HouseHolder", True)
    test_accuracy("GramSchmidt", True)