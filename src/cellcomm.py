import rpy2.robjects as robjects
from rpy2.robjects import pandas2ri
pandas2ri.activate()

readRDS = robjects.r['readRDS']
print('reading rds file ...')
df = readRDS('data/NewZsGreen7TPMerged_3333_ccmregression.rds')

print('Result:')
print(str(df))
print(repr(df))

print('...... keys ......')
# print(df.keys())
for key in df:
    print (key)
print('========================')
