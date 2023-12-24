import time
import pyttsx3
import speech_recognition as sr
import sqlite3

def initialize_database():
    connection = sqlite3.connect("speech_results.db")
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS speech_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        result TEXT,
        presence TEXT
    )
    """)

    connection.commit()
    connection.close()

def insert_result_into_database(result, presence):
    connection = sqlite3.connect("speech_results.db")
    cursor = connection.cursor()

    cursor.execute("INSERT INTO speech_results (result, presence) VALUES (?, ?)", (result, presence))
    connection.commit()
    connection.close()

def recognize_speech():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Please say Present or Absent:")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio_data = recognizer.listen(source, timeout=5)  # Increased timeout to 5 seconds

    try:
        # Use the Google Web Speech API to recognize the speech
        result = recognizer.recognize_google(audio_data)
        print("Google Web Speech API result:", result)
        return result.lower()
    except sr.UnknownValueError:
        print("Sorry, could not understand audio. Considering as Absent.")
        return "absent"
    except sr.RequestError as e:
        print("Error with the speech recognition service; {0}".format(e))
        return "absent"

def read_out_number_and_recognize():
    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    engine.setProperty('rate', 150)

    for number in range(1, 4):  # Adjusted the range for 3 roll numbers
        print(f"System: Roll Number {number}.")
        engine.say(f"Roll number {number}")
        engine.runAndWait()

        start_time = time.time()
        result = recognize_speech()
        elapsed_time = time.time() - start_time

        if "present" in result.lower():
            presence = "present"
        else:
            presence = "absent"

        if elapsed_time >= 5:
            print("Time exceeded. Marking as Absent.")
            presence = "absent"

        print("You said:", result)
        print("Marked as:", presence)

        # Insert the result and presence into the database
        insert_result_into_database(f"Roll number {number}", presence)

        time.sleep(1)

# Save results to a text file
def save_results_to_txt(results, file_path):
    with open(file_path, 'w') as file:
        file.write("Results from the database:\n")
        for row in results:
            file.write(f"ID: {row[0]}, Roll Number: {row[1]}, Presence: {row[2]}\n")

# Initialize the database
initialize_database()

# Perform the speech recognition and database operations
read_out_number_and_recognize()

# Display the results from the database
connection = sqlite3.connect("speech_results.db")
cursor = connection.cursor()
cursor.execute("SELECT * FROM speech_results")
results = cursor.fetchall()
connection.close()

# Save results to a text file
txt_file_path = r"/Users/praneeth/Desktop/Internship-1/attendance.txt"
save_results_to_txt(results, txt_file_path)

print(f"\nResults saved to: {txt_file_path}")