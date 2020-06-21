import math


class CosineSimilarity:
    def __init__(self):
        print("Cosine Similarity initialized")

    @staticmethod
    def cosine_similarity_of(vector1, vector2):

        # convert vectors to set to find common words as intersection
        common = set(vector1.keys()).intersection(set(vector2.keys()))

        dot_product = 0.0

        for i in common:
            if not i == 'id':
                # get amount of each common word for both vectors and multiply them then add them together.
                dot_product += vector1[i] * vector2[i]

        squared_sum_vector1 = 0.0
        squared_sum_vector2 = 0.0

        # get squared sum values of word counts from each vector.
        for i in vector1.keys():
            if not i == 'id':
                squared_sum_vector1 += vector1[i] ** 2

        for i in vector2.keys():
            if not i == 'id':
                squared_sum_vector2 += vector2[i] ** 2

        # calculate magnitude with squared sums.
        magnitude = math.sqrt(squared_sum_vector1) * math.sqrt(squared_sum_vector2)

        if not magnitude:
            return 0.0
        else:
            return float(dot_product) / magnitude

