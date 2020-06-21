import CosineSimilarity


class RecommendationEngine:
    def __init__(self):
        print("RecommendationEngine initialized")

    @staticmethod
    # vectorization of the profile cv in order to make calculation
    def profile_to_vector(profile):
        v_profile = {'id': profile['id'], 'total_experience': profile['total_experience'],
                     'stability': profile['stability'], 'location': profile['location'],
                     'backend': profile['backend'], 'frontend': profile['frontend'],
                     'phpsymfony': profile['phpsymfony'],
                     'ArchitecteJee': profile['ArchitecteJee'], 'Embedded': profile['Embedded'],
                     'fullstackjs': profile['fullstackjs'],
                     'java/jee': profile['java/jee'], 'DRUPAL': profile['DRUPAL'], 'PO': profile['PO']}
        if 'headline' in profile.keys():
            skill_keys = profile['headline'].keys()
            for key in skill_keys:
                v_profile[key] = 0
                v_profile[key] = profile['headline'][key] or profile['summary'][key] or profile['experience'][key] or \
                                 profile['skills'][key]
        return v_profile

    @staticmethod
    # This function returns n similar profiles of a single profile
    def get_similar_profiles(profile, profile_list, n):
        result_list = []
        for profile_v in profile_list:
            similarity = CosineSimilarity.CosineSimilarity.cosine_similarity_of(profile, profile_v)
            result_list.append({'id': profile_v['id'], 'similarity': similarity})
        return sorted(result_list, key=lambda i: i['similarity'], reverse=True)[:n]

