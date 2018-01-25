from hmmlearn.hmm import GaussianHMM
import numpy as np
from matplotlib import cm, pyplot as plt
import warnings
warnings.filterwarnings("ignore")


if __name__ == "__main__":
    X_train = np.loadtxt('/home/nino/PycharmProjects/rai_experiments/sinus/data/0/train.flat')
    X_test = np.loadtxt('/home/nino/PycharmProjects/rai_experiments/sinus/data/0/test.flat')
    length_train = X_train.shape[0]
    length_test = X_test.shape[0]
    length_sliding_window = 16
    n_components = 10
    number_sequence_train = length_train-length_sliding_window+1
    number_sequence_test = length_test-length_sliding_window+1
    X_slice_train = np.empty((number_sequence_train, length_sliding_window))
    X_slice_test = np.empty((number_sequence_test, length_sliding_window))

    # print X_slice.shape
    # print X_slice[0,:]
    # print X[0:0+length_sliding_window]
    for i in xrange(number_sequence_train):
        X_slice_train[i,:] = X_train[i:i+length_sliding_window]
    for i in xrange(number_sequence_test):
        X_slice_test[i,:] = X_test[i:i+length_sliding_window]
    X_slice_train = X_slice_train.flatten().reshape(number_sequence_train*length_sliding_window,1)#flatten training into one sequence with multiple sequences
    lengths = [length_sliding_window for i in xrange(number_sequence_train)]
    #print X_slice.shape
    print X_slice_test.shape
    print X_slice_test[0]
    print("fitting to HMM and decoding")

    # print "BAH", X_slice_train
    # print "BAH", lengths

    model = GaussianHMM(n_components, covariance_type="diag", n_iter=100).fit(X_slice_train, lengths)

    import dot_utility as du
    du.export_hmm_md(model, "/home/nino/PycharmProjects/rai_experiments/sinus/canc.dot")

    #print()
    ###############rolling prediction##########
    computed = list()
    for i in xrange(number_sequence_test):
        prob = model.predict_proba(X_slice_test[i,:].reshape(length_sliding_window,1))#probability of states in each time step
        prob_next_state = np.dot(prob[-1,:], model.transmat_)
        #print prob_next_state
        temp = 0
        for j in xrange(n_components):
            temp += prob_next_state[j]*model.means_[j]
        print i, temp
        computed.append(temp)

    plt.plot(computed, 'b')
    plt.plot(X_test[16:], 'r')
    plt.show()