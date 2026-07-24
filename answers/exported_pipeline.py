import sklearn
from sklearn.pipeline import Pipeline

pipeline = Pipeline(memory=None,
         steps=[('robustscaler',
                 RobustScaler(copy=True,
                              quantile_range=(0.2598372227484, 0.7911904578074),
                              unit_variance=False, with_centering=True,
                              with_scaling=True)),
                ('variancethreshold',
                 VarianceThreshold(threshold=0.0001303942753)),
                ('featureunion-1',
                 FeatureUnion(n_jobs=None,
                              transformer_list=[('featureunion',
                                                 FeatureUnion(n_jobs=None,
                                                              trans...
                              transformer_list=[('skiptransformer',
                                                 SkipTransformer()),
                                                ('passthrough', Passthrough())],
                              transformer_weights=None, verbose=False,
                              verbose_feature_names_out=True)),
                ('kneighborsclassifier',
                 KNeighborsClassifier(algorithm='auto', leaf_size=30,
                                      metric='minkowski', metric_params=None,
                                      n_jobs=1, n_neighbors=12, p=1,
                                      weights=np.str_('uniform')))],
         transform_input=None, verbose=False)
