"""""
Created on 12-Jan-2022, 13:30
By Mees van Stiphout
"""""

from auchann.align_words import align_words


def main(args=None):
    """
    TODO: how do we want this function to be implemented exactly?
    Currently this is the same as cli.py
    """

    try:
        while True:
            transcript = input("Transcript: ")
            correction = input("Correction: ")
            alignment = align_words(transcript, correction)
            print(alignment)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
