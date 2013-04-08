def atricle_classify():

	# For regular expressions, see http://docs.python.org/2/library/re.html

	# Feature example: whether the article contains the phrase "financial crisis".
	def contain_finantial_crisis(article):
		import re
		return (re.search(r"\bfinancial crisis\b", article, flags=re.IGNORECASE) != None)

	# Feature example: whether the article contains the phrase "financial responsibility".
	def contain_financial_responsibility(article):
		import re
		return (re.search(r"\bfinancial responsibility\b", article, flags=re.IGNORECASE) != None)
		
	# Defines the article feature set.
	def article_features(article):
		return {'contain_finantial_crisis': contain_finantial_crisis(article), 'contain_financial_responsibility': contain_financial_responsibility(article)}

		
	# Get all the manually classified articles (and their classification).
	# TODO: decide how the atricles and their classifications are given to me as input.
	article_classification = ([("financial crisis", "left")] + [("financial responsibility", "right")])
	
	# For every article, generate its feature set.
	featuresets = [(article_features(a), tag) for (a,tag) in article_classification]

	#print article_classification
	print featuresets
		
	# Splits the articles into a train set and a test set.
	# TODO: decide the sizes of these sets.
	train_set = featuresets[500:] 
	test_set = featuresets[:500]

	# Train the classifier based on the test set.
	# TODO: run on Linux after installing https://bitbucket.org/wcauchois/pysvmlight
	import nltk.classify.svm
	classifier = SvmClassifier.train(train_set)
		
	# Examples for statistics we can get for our trained classifier performance.
	print('--- Article Classifier ---')
	print('Number of training examples:', len(train_set))
	print('Total SVM dimensions:', len(classifier._svmfeatureindex))
	print('Label mapping:', classifier._labelmapping)
	print('--- Processing an example instance ---')
	print('Reference instance:', article_classification[0][0])
	print('NLTK-format features:\n	' + str(test_set[0]))
	print('SVMlight-format features:\n	' + str(map_instance_to_svm(test_set[0], classifier._labelmapping, classifier._svmfeatureindex)))
	distr = classifier.prob_classify(test_set[0][0])
	print('Instance classification and confidence:', distr.max(), distr.prob(distr.max()))
	print('--- Measuring classifier performance ---')
	print('Overall accuracy:', accuracy(classifier, test_set))
	
'''

# taken from http://nltk.org/_modules/nltk/classify/svm.html
def demo():

	from nltk.classify import accuracy
	from nltk.corpus import names

	# Get all the manually classified articles (and their class).
	import random
	names = ([(name, 'male') for name in names.words('male.txt')] +
			 [(name, 'female') for name in names.words('female.txt')])
	import random
	random.seed(60221023)
	random.shuffle(names)

	# For every article, generate its feature set.
	featuresets = [(gender_features(n), g) for (n,g) in names]
	
	# Splits the articles into a train set and a test set.
	train_set, test_set = featuresets[500:], featuresets[:500]

	print('--- nltk.classify.svm demo ---')
	print('Number of training examples:', len(train_set))
	
	# Train the classifier based on the test set.
	classifier = SvmClassifier.train(train_set)
	
	# Examples for statistics we can get for our trained classifier performance.
	print('Total SVM dimensions:', len(classifier._svmfeatureindex))
	print('Label mapping:', classifier._labelmapping)
	print('--- Processing an example instance ---')
	print('Reference instance:', names[0])
	print('NLTK-format features:\n	' + str(test_set[0]))
	print('SVMlight-format features:\n	' + str(map_instance_to_svm(test_set[0], classifier._labelmapping, classifier._svmfeatureindex)))
	distr = classifier.prob_classify(test_set[0][0])
	print('Instance classification and confidence:', distr.max(), distr.prob(distr.max()))
	print('--- Measuring classifier performance ---')
	print('Overall accuracy:', accuracy(classifier, test_set))
'''

if __name__ == '__main__':
	#demo()
	
	atricle_classify()

	# Test contain_finantial_crisis 
	'''Uncommenet for contain_finantial_crisis testing
	
	print contain_finantial_crisis("blah blah financial crisis. blah blah")					# true
	print contain_finantial_crisis("Financial crisis is the top issue today")				# true
	print contain_finantial_crisis("The Financial Crisis")									# true
	print contain_finantial_crisis("if the aspect is financial, crisis is not an option")	# false
	print contain_finantial_crisis("it's financial. Crisis is not...")						# false
	'''
