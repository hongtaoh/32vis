library(ggplot2)
library(dplyr)
library(scales)
library(tidyverse)
library(ggpubr)
library(ggridges)
library(data.table)
library(reshape2)
library(stargazer)
library('car')
library("olsrr")

df = read.csv('../data/ht_class/ht_cleaned_paper_df.csv')
df = df[df$Year <= 2020, ]
df$Year.Distance.from.2020 = abs(df$Year - 2020)

########## CONFERENCE TRACKS

fit <- aov(Number.of.Citations ~ Conference, data = df)
summary(fit)

## All pairs are significant except for vis-vast
TukeyHSD(fit, conf.level = 0.95)
plot(TukeyHSD((fit)))

###########
df <- mutate(df, citenum_non_zero = Number.of.Citations + 0.99)
df <- mutate(
  df, 
  gcitenum_non_zero = Citation.Counts.on.Google.Scholar + 0.99)
df <- mutate(df, citenum_log10 = log10(citenum_non_zero))
df <- mutate(df, gcitenum_log10 = log10(gcitenum_non_zero))

############ checking outliers
# core_vars<- c('Year', 
#               'Conference', 
#               'PaperType', 
#               'Number.of.Authors', 
#               'Cross.type.Collaboration', 
#               'Cross.country.Collaboration',
#               'With.US.Authors',
#               'Award',
#               'Number.of.Citations'
#               ) 
# indepdent_vars <- c('Year', 
#                     'Conference', 
#                     'PaperType', 
#                     'Number.of.Authors', 
#                     'Cross.type.Collaboration', 
#                     'Cross.country.Collaboration',
#                     'With.US.Authors',
#                     'Award') 
# outcome_vars <- c('Number.of.Citations')


########
model = lm(Number.of.Citations ~
             Year.Distance.from.2020 + Conference + PaperType
           + Number.of.Authors + Cross.type.Collaboration +
             Cross.country.Collaboration + With.US.Authors + Award,
           data = df)

# #### Diagnosis
# y_hat_obj<-predict(model)
# u_obj<-resid(model)
# s_u_obj<-rstandard(model)
# qqnorm(s_u_obj)
# abline(0,0,col='red')
# # mean(u_invst)
# shapiro.test(u_obj)
# 
# plot(y_hat_obj,s_u_obj)
# abline(0,0,col='red')

# should be below 5
car::vif(model)


## ALL IN ONE
ols_plot_resid_fit(model)
ols_coll_diag(model)

summary(model)

library(jtools)
plot_summs(model, 
           plot.distributions = FALSE, scale=FALSE) + theme_apa()
ggsave('../results/figures/supp_reg_openalex.pdf')

stargazer(model)

model1 = lm(citenum_log10 ~
              Year.Distance.from.2020 + Conference + PaperType
           + Number.of.Authors + Cross.type.Collaboration +
             Cross.country.Collaboration + With.US.Authors + Award,
           data = df)

summary(model1)

plot_summs(model1, 
           plot.distributions = FALSE, scale=FALSE) + theme_apa()
ggsave('../results/figures/supp_reg_openalex_log10.pdf')

stargazer(model1)

vif(model1)

ols_plot_resid_fit(model1)
ols_coll_diag(model1)

# model2 = lm(gcitenum_log10 ~
#               Year.Distance.from.2020 + Conference + PaperType
#             + Number.of.Authors + Cross.type.Collaboration +
#               Cross.country.Collaboration + With.US.Authors + Award,
#             data = df)
# 
# summary(model2)
# 
# vif(model2)
# 
# ols_plot_resid_fit(model2)
# ols_coll_diag(model2)

model3 = lm(Citation.Counts.on.Google.Scholar ~
              Year.Distance.from.2020 + Conference + PaperType
           + Number.of.Authors + Cross.type.Collaboration +
             Cross.country.Collaboration + With.US.Authors + Award,
           data = df)
summary(model3)

vif(model3)

plot_summs(model3, 
           plot.distributions = FALSE, scale=FALSE) + theme_apa()
ggsave('../results/figures/supp_reg_gscholar.pdf')

stargazer(model3)

# df <- mutate(df, citenum_non_zero = Number.of.Citations + 0.99)

######################################### PLOTS

# ggplot(df, aes(x = citenum_non_zero, y = Award)) + 
#   geom_density_ridges() + 
#   scale_x_continuous(
#     trans = 'log10',
#     breaks=trans_breaks('log10', function(x) 10^x),
#     labels=trans_format('log10', math_format(10^.x))
#   )
# 
# dff <- subset(df, select=c('citenum_non_zero', 
#                     'Cross.type.Collaboration', 
#                     'Cross.country.Collaboration',
#                     'With.US.Authors', 
#                     'Award'))
# 
# long <- melt(dff, id.vars = c('citenum_non_zero'))
# type <- paste(toString(long$variable), 
#                    toString(long$value),
#                    sep = "_"
#                      )
# long$type = type

# ggplot(long, aes(x = citenum_non_zero, y = type)) + 
#   geom_density_ridges() + 
#   scale_x_continuous(
#     trans = 'log10',
#     breaks=trans_breaks('log10', function(x) 10^x),
#     labels=trans_format('log10', math_format(10^.x))
#   )