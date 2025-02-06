import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.stem.porter import PorterStemmer
import ast

dfm = pd.read_csv('tmdb_5000_movies.csv')
dfc = pd.read_csv('tmdb_5000_credits.csv')


df = dfm.merge(dfc, on='title')

df = df[['genres','id','keywords','title','overview','cast','crew']]

df.dropna(inplace=True)

def convert(obj):
    L = []
    for i in ast.literal_eval(obj):
        L.append(i['name'])
    return L

df['genres'] = df['genres'].apply(convert)
df['keywords'] = df['keywords'].apply(convert)

def convert_3(obj):
    L = []
    for i in ast.literal_eval(obj):
        if len(L) < 3:
            L.append(i['name'])
    return L

df['cast'] = df['cast'].apply(convert_3)

def fetch_director(obj):
    for i in ast.literal_eval(obj):
        if i['job'] == 'Director':
            return [i['name']]
    return []

df['crew'] = df['crew'].apply(fetch_director)
df = df.rename(columns={'crew':'Director'})

df['overview'] = df['overview'].apply(lambda x: x.split())

for column in ['genres', 'keywords', 'overview', 'cast', 'Director']:
    df[column] = df[column].apply(lambda x: [i.replace(' ','') for i in x])

df['tags'] = df['genres'] + df['keywords'] + df['overview'] + df['cast'] + df['Director']

final_df = df[['id','title','tags']]

final_df['tags'] = final_df['tags'].apply(lambda x: ' '.join(x).lower())

ps = PorterStemmer()

def stem(text):
    return ' '.join([ps.stem(word) for word in text.split()])

final_df['tags'] = final_df['tags'].apply(stem)

# Vectorizing the data
cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(final_df['tags']).toarray()

# Calculating cosine similarity
similarity = cosine_similarity(vectors)

def recommend(movie):
    try:
        movie_index = final_df[final_df['title'] == movie].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
        
        return [final_df.iloc[i[0]].title for i in movies_list]
        
    except IndexError:
        return [f'{movie} not found']

print(recommend('Iron Man 2'))

import pickle

# Save the final dataframe
final_df.to_pickle('final_df.pkl')

# Save the similarity matrix
with open('similarity.pkl', 'wb') as f:
    pickle.dump(similarity,f)

print("Pickle files saved successfully!")