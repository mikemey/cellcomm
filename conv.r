library(sp)

print('reading rds...')
x <- readRDS("data/NewZsGreen7TPMerged_3333_ccmregression.rds")

print('writing file...')
write.csv(x, file = "ccmregression.csv")