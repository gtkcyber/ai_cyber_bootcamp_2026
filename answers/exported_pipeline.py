import sklearn
from sklearn.pipeline import Pipeline

pipeline = Pipeline(memory=None,
         steps=[('robustscaler',
                 RobustScaler(copy=True,
                              quantile_range=(0.0064903926995, 0.7721076958927),
                              unit_variance=False, with_centering=True,
                              with_scaling=True)),
                ('selectfwe',
                 SelectFwe(alpha=0.0006118770943,
                           score_func=<function f_classif at 0x11a63f740>)),
                ('featureunion-1',
                 FeatureUnion(n_jobs=None,
                              transformer_list=[('featureunion',
                                                 Featur...
                              transformer_list=[('skiptransformer',
                                                 SkipTransformer()),
                                                ('passthrough', Passthrough())],
                              transformer_weights=None, verbose=False,
                              verbose_feature_names_out=True)),
                ('kneighborsclassifier',
                 KNeighborsClassifier(algorithm='auto', leaf_size=30,
                                      metric='minkowski', metric_params=None,
                                      n_jobs=1, n_neighbors=29, p=1,
                                      weights=np.str_('uniform')))],
         transform_input=None, verbose=False)
