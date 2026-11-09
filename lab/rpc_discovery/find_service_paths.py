import re

with open(r"C:\Users\cochr\.gemini\bin\agy.exe", "rb") as f:
    data = f.read()

# Search for /<something>/ConvertTrajectoryToMarkdown or /<something>/GetTrajectoryTurns
matches = re.findall(rb'/[a-zA-Z0-9_\.]+/ConvertTrajectoryToMarkdown', data)
print("ConvertTrajectory matches:", matches)

matches2 = re.findall(rb'/[a-zA-Z0-9_\.]+/GetTrajectoryTurns', data)
print("GetTrajectoryTurns matches:", matches2)

matches3 = re.findall(rb'/[a-zA-Z0-9_\.]+/GetConversationMetadata', data)
print("GetConversationMetadata matches:", matches3)

matches4 = re.findall(rb'/[a-zA-Z0-9_\.]+/GetCascadeTrajectory', data)
print("GetCascadeTrajectory matches:", matches4)

