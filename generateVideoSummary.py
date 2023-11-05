import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import openai
import json
import networkx as nx

# OpenAI API key
openai.api_key = "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"

def callOpenAPI(prompt):
    # Makes a call to the OpenAI API using the prompt that we define
    print(prompt)
    completion = openai.Completion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return completion['choices'][0]['message']['content']

def promptForYTDescription(title, description):
    # Returns the prompt that we'd use for calling the GPT model for generating a concise YT video description
    return 'Generate a content description for my YouTube video with the title ' + str(title) + ' using the existing description as a reference. Make the new description more engaging and informative. This description should not be more than 2 sentences long. It should only contain the most relevant and the most important information. Please provide a well-structured and attention-grabbing description.\nHere\'s the video description:' + str(description)

def promptForVideoSummarization(transcriptions, properDescription):
    # Returns a brief summarization for the youtube video. The summary is dividied into different section and involves info about title, text, start, and end times
    transcriptionsText = transcriptions.to_csv(sep='\t', header=False, index=False, line_terminator='\n')

    prompt = '''I will provide you with the transcripted data of a youtube video. This transcripted data is of the format start time, end time, and text. This youtube video is ${properDescription}. I want you to only return those start time, end time, and text tuples that are the most relevant to the given video and also summarize the entire content in a brief manner.  You should make sure that you are covering the important details of the solution and the derivations as well. Make sure that each point in the returned output has a title, start time, end time, and the text.

    Here are the video transcriptions
    ${transcriptions}

    I am also providing you with the sample answers for two different videos so you know the expected format.

    Sample answer 1:
    1. Introduction to the Putnam competition:
       - Start: 0 seconds
       - End: 13 seconds
       - Text: An introduction to the Putnam competition, a challenging math competition for undergraduate students with 12 questions.

    2. The Challenging Problem:
       - Start: 72 seconds
       - End: 96 seconds
       - Text: The main problem discussed in the video is introduced - If you choose four random points on a sphere and consider the tetrahedron with these points as its vertices, what is the probability that the center of the sphere is inside that tetrahedron?

    3. Two-Dimensional Case:
       - Start: 114 seconds
       - End: 135 seconds
       - Text: Simplifying the problem by considering a two-dimensional case where three random points are chosen on a circle.

    4. Probability in Two Dimensions:
       - Start: 179 seconds
       - End: 224 seconds
       - Text: Explaining the probability calculation in two dimensions, where the average probability that the triangle contains the center of the circle is determined.

    5. Extension to Three Dimensions:
       - Start: 266 seconds
       - End: 283 seconds
       - Text: Extending the problem to three dimensions and explaining how to calculate the probability for the tetrahedron containing the center of the sphere.

    6. Elegant Insight:
       - Start: 345 seconds
       - End: 383 seconds
       - Text: Discussing the elegant insight of reframing the problem and thinking about choosing lines and points instead of random points.

    7. General Problem-Solving Approach:
       - Start: 391 seconds
       - End: 435 seconds
       - Text: Providing a general problem-solving approach by breaking down complex problems into simpler cases and looking for key insights.

    8. Sponsor Message - Brilliant.org:
       - Start: 575 seconds
       - End: 621 seconds
       - Text: Promoting Brilliant.org as a platform for enhancing problem-solving skills and presenting a probability puzzle related to cheating students.

    9. Conclusion:
       - Start: 668 seconds
       - End: 671 seconds
       - Text: Concluding remarks and closing the video.

    Sample answer 2:
    1. Introduction
       - Start: 0.0
       - End: 2.88
       - Text: Thank you to Audible for making this video possible.

    2. Video Introduction
       - Start: 3.38
       - End: 4.88
       - Text: Hi everyone, Jade here.

    3. Introduction to P vs. NP
       - Start: 4.88
       - End: 10.26
       - Text: Today\'s video is about a problem that has often been called the biggest unsolved problem in computer science. P versus NP.

    4. Definition of P vs. NP
       - Start: 10.26
       - End: 17.1
       - Text: It can roughly be translated to, if a problem is easy to check the solution to, is it also easy to find the solution to?

    5. Overview of Video Content
       - Start: 27.92
       - End: 30.84
       - Text: So in this video, we\'re going to see what all the hype is about, why it\'s even a question in the first place, and a whole lot more about the nature of computer science.

    6. Introduction to the "Numbers Grabble" Game
       - Start: 35.62
       - End: 40.36
       - Text: We\'re going to start in a somewhat unexpected place by playing a game. This game is called Numbers Grabble, and it\'s you versus me.

    7. Explanation of Magic Square and Tic-Tac-Toe
       - Start: 78.3
       - End: 111.0
       - Text: When we arrange numbers gravel in a magic square, we see it\'s really the same game as tic-tac-toe.

    8. Introduction to Algorithms
       - Start: 144.88
       - End: 150.64
       - Text: In math and computer science, these strategies are called algorithms, and they\'re mechanical procedures, kind of like a recipe.

    9. Computational Complexity
       - Start: 169.16
       - End: 177.6
       - Text: How complicated an algorithm a problem needs to solve is one of the main areas of interest in computer science.

    10. Explanation of Complexity Classes P and NP
        - Start: 180.64
        - End: 189.24
        - Text: P and NP are just classes of problems based on how difficult they are to solve.

    11. Difference between P and NP
        - Start: 194.35999999999999
        - End: 259.32
        - Text: P is the class of all problems which have an algorithm that can be computed in polynomial time, while NP problems may take an exponential number of steps to solve.

    12. Significance of P vs. NP Question
        - Start: 310.96000000000004
        - End: 320.0
        - Text: The question does P equal NP? Is asking whether these two complexity classes, P and NP are in fact the same class?

    13. Challenges and Ambiguity
        - Start: 338.68
        - End: 346.0
        - Text: Why is this even a question? I mean, for something to be called the biggest open problem in computer science, there needs to be some kind of ambiguity around the answer.

    14. Potential Impact of P equals NP
        - Start: 408.64
        - End: 472.56
        - Text: If P were equal to NP, then the world would be a profoundly different place. It would be pretty cool if P did equal NP. Being able to solve any problem just as easy as checking the solution would make life insanely easier.

    15. Discussion of Algorithmic Improvements
        - Start: 514.96
        - End: 602.72
        - Text: Sometimes you can improve an algorithm so that it solves a problem faster. The point of all of this is that sometimes you can improve an algorithm so that it solves a problem faster.

    16. Explaining Complexity Classes
        - Start: 659.7199999999999
        - End: 719.24
        - Text: Complexity classes aren\'t like totally separate things. The question of whether P equals NP still isn\'t solved because this NP refers to NP complete problems.

    17. The Significance of P vs. NP Question
        - Start: 764.68
        - End: 807.76
        - Text: If just one of the NP complete problems was shown to be in the class P, that would mean that all of the NP complete problems would be in the class of P.

    18. Recommendation and Sponsor
        - Start: 816.36
        - End: 832.96
        - Text: I can recommend some interesting books to you. Today\'s video is sponsored by Audible.

    19. Conclusion and Summary
        - Start: 848.84
        - End: 854.04
        - Text: So, that\'s it. That\'s P vs. NP, the biggest open problem in computer science.

    Sample Answer 3:
    Here are the most relevant parts of the transcript for the video "Discover the accidental birth of computer science through the fascinating history of Turing Machines":

    1. Introduction to Computer Science:
       - Start: 0.0 seconds
       - End: 6.16 seconds
       - Text: Hi everyone, Jade here. Today\'s video is an origin story about the entire field of computer science.

    2. The Scope of Computer Science:
       - Start: 6.16 seconds
       - End: 17.68 seconds
       - Text: Now when I say computer science, I mean literally everything to do with computers. Laptops, desktops, smartphones, iPods, GPSs, quantum computers, literally every physical manifestation of a computer you can think of. But I also mean the theoretical side too.

    3. The Question About the Foundations of Mathematics:
       - Start: 38.08 seconds
       - End: 44.16 seconds
       - Text: This story highlights an incredible turn of events, a brilliant thinker, and the interconnectedness of two fields. The story starts with an extraordinary man named David Hilbert. He lived at a very exciting time in the history of mathematics. See, back in the 1900s, it had come to light that no one was really sure what they were studying when they were studying mathematics.

    4. Different Views on Mathematics:
       - Start: 66.24 seconds
       - End: 101.04 seconds
       - Text: When we study biology, we\'re studying living things that exist in the real world. When we study physics, we\'re studying real-world phenomena which we can verify via experiment. But math, was it the study of real-world objects or abstract entities? Did it exist in our minds or in some other realm of existence?

    5. Hilbert\'s Approach:
       - Start: 101.04 seconds
       - End: 129.2 seconds
       - Text: Hilbert thought that if we treat math as nothing more than a formal system, there could be no more disagreements about what was and wasn\'t allowed.

    6. Turing\'s Involvement:
       - Start: 330.8 seconds
       - End: 346.08 seconds
       - Text: At the young age of 22, Churring got intensely interested in his last question, decidability. Did there exist an effective procedure for deciding the truth or falsity of any mathematical statement?

    7. Churring\'s Definition of an Effective Procedure:
       - Start: 346.08 seconds
       - End: 381.12 seconds
       - Text: But Churring saw a slight problem with the question. What exactly was an effective procedure? Today, an effective procedure is considered to be an algorithm, some step-by-step set of instructions that you can follow without using any real thought or intuition.

    8. The Birth of Computer Science:
       - Start: 781.52 seconds
       - End: 824.1600000000001 seconds
       - Text: This birthed the entire field of computer science, which is the study of what computers can and can\'t do, the complexity of algorithms, and the overall nature of computation.

    9. The Influence of Turing Machines:
       - Start: 815.7600000000001 seconds
       - End: 824.1600000000001 seconds
       - Text: Anything from your desktop to your smartphone to the computers on the International Space Station are based on Cheering\'s model.

    10. Current State of Computer Science:
        - Start: 825.6 seconds
        - End: 835.44 seconds
        - Text: Now it\'s worth noting that other models of computation do exist. A Lanzo Church who would later become Cheering\'s doctoral advisor actually came up with his own model just weeks before Cheering, called the Lambda Calculus.

    11. Future Possibilities:
        - Start: 898.64 seconds
        - End: 910.08 seconds
        - Text: The trouble is making them physically realizable. Another model of computation that\'s been getting a lot of hype recently are quantum computers, which if they work, will definitely bring something new to the table.

    12. Conclusion:
        - Start: 966.96 seconds
        - End: 1003.68 seconds
        - Text: If you\'d like to check it out and support the channel, go to brilliant.org slash up and atom.'''

    # Replacing the place-holder strings to make sure that things work as expected
    prompt.replace("${properDescription}", properDescription)
    prompt.replace("${transcriptions}", transcriptionsText)

    return prompt

def summarize(transcriptions, metadata):
    # Get the proper description for the youtube video
    properDescriptionPrompt = promptForYTDescription(metadata["title"], metadata["description"])
    properDescription = callOpenAPI(properDescriptionPrompt)

    # Get the summary for the youtube video using the above prompt. Transcriptions is a pandas dataframe having start, end, text
    summaryPrompt = promptForVideoSummarization(transcriptions, properDescription)
    summary = callOpenAPI(summaryPrompt)

    # Get the CSV file for the above textual summary
    csvGenerationPrompt = 'Convert the above summary into a CSV file. The format should be - Title, start, end, text'
    csvData = callOpenAPI(csvGenerationPrompt)
    print(csvData)

    return csvData

def elaborate(text):
    #! TODO
    prompt = ""
    pass

def main():
    metadata = {
        "title": "Why Pure Information Gives Off Heat",
        "description": '''Sign up to Brilliant to receive a 20 percentage discount with this link! https://brilliant.org/upandatom/

        Hi! I'm Jade. If you'd like to consider supporting Up and Atom, head over to my Patreon page :) 

         / upandatom  

        Visit the Up and Atom store
        https://store.nebula.app/collections/...

        Subscribe to Up and Atom for physics, math and computer science videos
          

         / upandatom  

        Why Time Actually Flows Both Ways
          

        - Why Time Actually Flows Both Ways  

        Follow me @upndatom

        Up and Atom on Twitter: https://twitter.com/upndatom?lang=en

        Up and Atom on Instagram:  

         / upndatom  

        For a one time donation, head over to my PayPal :)  https://www.paypal.me/upandatomshows

        A big thank you to my AMAZING PATRONS!
        Michael Seydel, Cy 'kkm' K'Nelson
        , Rick DeWitt, Thorsten Auth
        , Purple Penguin
        , AndrewA, Izzy Ca, bpatb
        , Michael Martin, Scott Ready, 
        John H. Austin, Jr.
        , Brian Wilkins, Thomas V Lohmeier, David Johnston
        ,  
        Thomas Krause
        , Yana Chernobilsky, 
        Lynn Shackelford, Ave Eva Thornton, 
        Andrew Pann, 
        Anne Tan
        , James Mahoney, Jim Felich,  Fabio Manzini, Jeremy, Sam Richardson, Robin High, KiYun Roe, Christopher Rhoades, DONALD McLeod, Ron Hochsprung, OnlineBookClub.org, Aria Bend, James Matheson, Robert A Sandberg, Kevin Anderson, Tim Ludwig, Alexander Del Toro Barba, Corey Girard, Justin Smith, Emily, A. Duncan, Mark Littlehale, Lucas Alexander, Jan Gallo, Tony T Flores, 
        Jeffrey Smith
        , Alex Hackman
        , Joel Becane, 
        Michael Hunter
        , Paul Barclay, 12tone, 
        Zhong Cheng Wang, 
        Sergey Ten, Damien Holloway, 
        Mikely Whiplash
        , John Lakeman
        , Jana Christine Saout
        , Jeff Schwarz
        , George Fletcher, 
        Louis Mashado, 
        Michael Dean
        , Chris Amaris, 
        Matt G
        , 
        Broos Nemanic
        , Dag-Erling Smørgrav
        , John Shioli
        , Joe Court
        , Todd Loreman
        , Susan Jones, Richard Vallender, jacques magraith, William Toffey, Michel Speiser, Rigid Designator, James Horsley, Bryan Williams, Craig Tumblison, Rickey Estes, Cameron Tacklind, 之元 丁, Kevin Chi, Paul Blanchard, Lance Ahmu, Tim Cheseborough, Nico Papanicolaou, keine, Markus Lindström, Jeffrey Melvin, Midnight Skeptic, Kyle Higgins, aeidolos, Mike Jepson, Dexter Scott, Potch, Thomas P Taft, Indrajeet Sagar, Markus Herrmann (trekkie22), Gil Chesterton, Alipasha Sadri, Pablo de Caffe, Alexander230, Taylor Hornby, Eric Van Oeveren, Mark Fisher, Phizz, Rudy Nyhoff, Colin Byrne, Nick H, Jesper de Jong, Loren Hart, Ari Prasetyo, Sofia Fredriksson, Phat Hoang, Spuddy, Sascha Bohemia, tesseract, Stephen Britt, KG, Dagmawi Elehu, Hansjuerg Widmer, John Sigwald, Carlos Gonzalez, Jonathan Ansell, Thomas Kägi, James Palermo, Gary Leo Welz,  Chris Teubert, Fran, Joe, Robert J Frey, The Doom Merchant, Wolfgang Ripken, Jeremy Bowkett, Vincent Karpinski, Nicolas Frias, Louis M, kadhonn, Moose Thompson, Andrew, Sam Ross, Garrett Chomka, Bobby Butler, Rebecca Lashua, Pat Gunn, Elze Kool, RobF, Vincent Seguin, Shawn, Israel Shirk, Jesse Clark, Steven Wheeler, Philip Freeman, KhAnubis, Jareth Arnold, Simon Barker, Dennis Haupt, Lou, amcnea, Simon Dargaville, and Magesh.

        Creator - Jade Tan-Holmes
        Script - Jack Johnson
        Animations - Standard Productions
        Music - epidemic sound
        '''
    }

    transcriptions = pd.read_csv('testingData/temp.tsv', sep = '\t')

    summarize(transcriptions, metadata)

main()

