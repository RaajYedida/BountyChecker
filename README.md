# WFBountyCheckerMacOS
A tool to check Cetus Bounties in Real Time on MacOS

# How does this work?
It reads and parses your EE.log

# Will I get banned for this?
Short Answer is: no.
Long Answer is: The Scripts parse EE.log, the logfile where Warframe logs all sorts of stuff, also bounty stages. A lot of 3rd parts Apps (such as YATE, Alecaframe and PTAnalyzer) use this to work. So far I am not aware of anyone being banned, but use at your own risk as any other program. 

# Changes
Changed the directory on warframe ee.log file location and commented out the pyttsx3 libraries as they were causing issues on MacOS

# Setup
- Download repository as a zip
- Extract
- Open Crossover or wine bottle's C: Drive folder
- Navigate to `/Users/Crossover (default username)/AppData/Warframe/EE.log` and copy the file path by holding down the option key
- Open `BountyChecker.py` with TextEditor or IDE of your choice
- Replace path on Line 51


# How to get the .py working?
Install Python 3.12.4 (this is what is has been tested on, may work on lower versions too). Then do `py -m pip install -r requirements.txt` in the folder.
Run via VS Code or Terminal 

# Issues
- Will not work when playing on Fullscreen/Windowed Fullscreen **MUST** be in Windowed mode for the overlay to show up due to how crossover bottles work or have to use a second monitor if you want to play on Fullscreen/Windowed Fullscreen
- using pyttsx3 crashes the window so no narration

I will be working on a fix on both of these issues as well as compiling this into a simple script so its easier to install
