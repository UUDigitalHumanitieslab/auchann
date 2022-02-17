from fileinput import close
import re
import editdistance
from editdistance import distance
import numpy as np

def match_word(corrected_word, counter, correction_dict, transcript_dict, transcript, distarray):
    if min(distarray) >= len(corrected_word):
        """
        if the edit distance is equal to or greater than the word itself, it's probably not a match
        """
        correction_dict[(corrected_word, counter)] = False
        matched_index = False
        return matched_index, correction_dict, transcript_dict
    else:
        matched_index = np.where(distarray == np.amin(distarray))[0]  # finds the shortest edit distance
        """
        if one corrected word has an equal edit distances for two or more transcript words, pick the word that has the closest index
        """
        if len(matched_index) > 1:  # if several transcript words have the same edit distance to the correction
            index_distances = np.abs(matched_index - counter)  # an array of distances of the matched words' indexes to the corrected word index
            closest_index = np.where(index_distances == np.amin(index_distances))[0]  # pick the one that is closest to original index
            """
            if several words are equally far apart from the correction, and have the same edit distance, pick the one that isn't taken yet, and otherwise default to the first one
            """
            if len(closest_index) > 1:

                # if the first word is still free, match it
                if transcript_dict[(transcript[matched_index[closest_index[0]]], matched_index[closest_index[0]])] == False:
                    matched_index = matched_index[closest_index[0]]
                    return matched_index, correction_dict, transcript_dict

                # if the second word is still free, match that
                elif transcript_dict[(transcript[matched_index[closest_index[1]]], matched_index[closest_index[1]])] == False:
                    matched_index = matched_index[closest_index[1]]
                    return matched_index, correction_dict, transcript_dict

                # if both are taken, but the edit distance of one is higher than the current edit distance
                elif transcript_dict[(transcript[matched_index[closest_index[0]]], matched_index[closest_index[0]])][3] > min(distarray):
                    corrword, corrindex = transcript_dict[(transcript[matched_index[closest_index[0]]], matched_index[closest_index[0]])][1], transcript_dict[(transcript[matched_index[closest_index[0]]], matched_index[closest_index[0]])][2]
                    correction_dict[(corrword, corrindex)] = False
                    matched_index = closest_index[0]
                    return matched_index, correction_dict, transcript_dict

                 # if both are taken, but the edit distance of the other is higher than the current edit distance
                elif transcript_dict[(transcript[matched_index[closest_index[1]]], matched_index[closest_index[1]])][3] > min(distarray):
                    corrword, corrindex = transcript_dict[(transcript[matched_index[closest_index[1]]], matched_index[closest_index[1]])][1], transcript_dict[(transcript[matched_index[closest_index[1]]], matched_index[closest_index[1]])][2]
                    correction_dict[(corrword, corrindex)] = False
                    matched_index = closest_index[0]
                    return matched_index, correction_dict, transcript_dict
                
                else:
                    second_best_distarray = distarray
                    for position in matched_index: 
                        second_best_distarray[position] = 999
                    matched_index, correction_dict, transcript_dict = match_word(corrected_word, counter, correction_dict, transcript_dict, transcript, second_best_distarray)
                    return matched_index, correction_dict, transcript_dict

            else:  # if one word is closer
                if transcript_dict[(transcript[matched_index[closest_index[0]]], matched_index[closest_index[0]])] == False:  # if the word is free, match it                    
                    matched_index = matched_index[0]
                    return matched_index, correction_dict, transcript_dict
                elif transcript_dict[(transcript[matched_index[closest_index[0]]], matched_index[closest_index[0]])][3] > min(distarray):  # if the edit distance of the pre-matched word is higher than the current smallest edit distance, replace the match with the current word
                    corrword, corrindex = transcript_dict[(transcript[matched_index[closest_index[0]]], matched_index[closest_index[0]])][1], transcript_dict[(transcript[matched_index[closest_index[0]]], matched_index[closest_index[0]])][2]
                    correction_dict[(corrword, corrindex)] = False

                    matched_index = matched_index[closest_index[0]]
                    return matched_index, correction_dict, transcript_dict
                    #####  REMATCH THE REPLACED WORD  -- or do I do that by recursion?  #####
                else:  # if the edit distance is smaller in the pre-matched word, find the second best ED or second closest index
                    """
                    create a second array of edit distances, this time with the smallest distances 'made unavailable': i.e. bumped up to 999 so that the indexes can still be seen but will not be taken into account
                    """
                    second_best_distarray = distarray
                    for position in matched_index: 
                        second_best_distarray[position] = 999
                    matched_index, correction_dict, transcript_dict = match_word(corrected_word, counter, correction_dict, transcript_dict, transcript, second_best_distarray)
                    return matched_index, correction_dict, transcript_dict


        else:  # if there is a single transcript word with the lowest edit distance
            if transcript_dict[(transcript[matched_index[0]], matched_index[0])] == False:  # if the word is free, match it                    
                matched_index = matched_index[0]
                return matched_index, correction_dict, transcript_dict
            elif transcript_dict[(transcript[matched_index[0]], matched_index[0])][3] > min(distarray):  # if the edit distance of the pre-matched word is higher than the current smallest edit distance, replace the match with the current word
                corrword, corrindex = transcript_dict[(transcript[matched_index[0]], matched_index[0])][1], transcript_dict[(transcript[matched_index[0]], matched_index[0])][2]
                correction_dict[(corrword, corrindex)] = False

                matched_index = matched_index[0]
                return matched_index, correction_dict, transcript_dict
                #####  REMATCH THE REPLACED WORD  -- or do I do that by recursion?  #####
            else:  # if the edit distance is smaller in the pre-matched word, find the second best ED or second closest index
                """
                create a second array of edit distances, this time with the smallest distances 'made unavailable': i.e. bumped up to 999 so that the indexes can still be seen but will not be taken into account
                """
                second_best_distarray = distarray
                for position in matched_index: 
                    second_best_distarray[position] = 999
                matched_index, correction_dict, transcript_dict = match_word(corrected_word, counter, correction_dict, transcript_dict, transcript, second_best_distarray)
                return matched_index, correction_dict, transcript_dict



def align_words(transcriptstring: str(), correctionstring: str(), transcript_dict = None, correction_dict = None, repeat = None):
    transcript = transcriptstring.split()  # split strings into list
    correction = correctionstring.split()

    if repeat is None:
        repeat = 2
    elif repeat > 0:
        repeat -= 1
    else:
        return transcript_dict, correction_dict
    
    ### To Do: 
    ## Make it so that one word cannot be matched to two words.
    """
    These dictionaries keep track of whether words in the transcript have already been matched to words in the correction, as well as the edit distance to the matched word
    Format= (word, index) : (matched (True/False), matched word, matched index, edit_distance)    
    """
    if transcript_dict is None:  # if no matching dictionary is provided, initialize here
        transcript_dict = {}
        for counter, word in enumerate(transcript):
            transcript_dict[(word, counter)] = False

    if correction_dict is None:  # if no matching dictionary is provided, initialize here
        correction_dict = {}
        for counter, word in enumerate(correction):
            correction_dict[(word, counter)] = False


    for counter, corrected_word in enumerate(correction):
        if correction_dict[(corrected_word, counter)] == False:  # if word in correction has not been matched yet try to match it
            """
            Try and match the correction word to a transcript word by looking at edit distances
            """
            distarray = np.empty(int())
            for transcribed_word in transcript:
                distarray = np.append(distarray, editdistance.eval(corrected_word, transcribed_word))  # get edit distances for each transcript word

            matched_index, correction_dict, transcript_dict = match_word(corrected_word, counter, correction_dict, transcript_dict, transcript, distarray)      
            if matched_index is False:
                pass
            else:
                matched_word = transcript[matched_index]
                correction_dict[(corrected_word, counter)] = (True, matched_word, matched_index, min(distarray))  # Fill the correction dict with Matched word, index, and distance
                transcript_dict[(matched_word, matched_index)] = (True, corrected_word, counter, min(distarray))  # Fill the transcription dict with Matched word, index and distance
                
        else:  # if the corrected word has already been matched, skip it.
            pass
    
    # for key in correction_dict:
    #     print(key, correction_dict[key])
    # print("\n")
    # for key in transcript_dict:
    #     print(key, transcript_dict[key])
    # print("\n")
    transcript_dict, correction_dict = align_words(transcriptstring, correctionstring, transcript_dict, correction_dict, repeat)
    
    return transcript_dict, correction_dict