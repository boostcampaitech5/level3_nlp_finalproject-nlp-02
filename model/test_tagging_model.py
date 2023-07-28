import torch
import random

def get_tag_from_model(content):
    random_number = random.randint(1, 100)
    
    if random_number < 10:
        test_tags = "Travel, Jeju, Island, Summer"
    elif random_number < 40:
        test_tags = "Mental, Healing, Care, Book, Therapy"
    elif random_number < 80:
        test_tags = "Daegu, Food, Travel, Makchang, Date"
    else:
        test_tags = "Theater, Movie, Marvel, Plot, Spiderman"
    
    return test_tags