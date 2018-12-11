import os
import datetime
import logger
import multiprocessing as mp

import numpy as np

from start import entry_point
import calibrationscore

# Rename files
LOG_TYPES = 'operational contracts cash reinoperational reincontracts reincash premium'.split(' ')
timestamp = datetime.datetime.now().strftime('%Y_%h_%d_%H_%M')
for log_type in LOG_TYPES:
    fname = 'data/one_%s.dat' % log_type
    try:
        os.rename(fname, fname + timestamp)
    except FileNotFoundError:
        print('file not found:', fname)

# Now run the ensemble

N = 300
PROCS = 4
# separate into PROCS procceses
epochs = np.array_split(np.arange(N), PROCS)
print([list(e) for e in epochs])
manager = mp.Manager()
par_logs = manager.list()

def _fn(_epoch):
    logs = [entry_point(('--replicid %d --replicating --oneriskmodel --multiprocess' % i).split(' ')) for i in _epoch]
    par_logs.append(logs)

procs = []
for epoch in epochs:
    proc = mp.Process(target=_fn, args=(epoch,))
    proc.start()
    procs.append(proc)

for p in procs:
    p.join()

for logs in par_logs:
    for log in logs:
        L = logger.Logger()
        L.restore_logger_object(log)
        L.save_log(True)

        CS = calibrationscore.CalibrationScore(L)
        score = CS.test_all()
