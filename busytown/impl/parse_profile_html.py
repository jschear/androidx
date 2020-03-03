#!/usr/bin/python3
 #
 # Copyright (C) 2016 The Android Open Source Project
 #
 # Licensed under the Apache License, Version 2.0 (the "License");
 # you may not use this file except in compliance with the License.
 # You may obtain a copy of the License at
 #
 #      http://www.apache.org/licenses/LICENSE-2.0
 #
 # Unless required by applicable law or agreed to in writing, software
 # distributed under the License is distributed on an "AS IS" BASIS,
 # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 # See the License for the specific language governing permissions and
 # limitations under the License.
 #
import argparse
import json
import os

# This script parses a profile .html report that was generated by Gradle and generates a machine-readable summary

def main():
  parser = argparse.ArgumentParser(
     description = "Parses a performance profile file generated by Gradle"
  )
  parser.add_argument("--input-profile", required=True, dest="input_profile")
  parser.add_argument("--output-summary", required=True, dest="output_summary")
  args = parser.parse_args()
  summarize(args.input_profile, args.output_summary)

def summarize(inputProfilePath, outputSummaryPath):
  # mapping from the key in the Gradle report to the key in the summary that we generate
  mapping = {"Total Build Time": "task_execution_duration", "Task Execution": "total_cpu", "Configuring Projects": "configuration_duration"}
  parsedValues = parse(inputProfilePath, mapping.keys())
  outputValues = dict()
  for k in mapping:
    if k in parsedValues:
      outputValues[mapping[k]] = parsedValues[k]
    else:
      raise Exception("Did not find key " + k + " in " + inputProfilePath + "; only found " + str(parsedValues))
  os.makedirs(os.path.dirname(outputSummaryPath), exist_ok=True)
  with open(outputSummaryPath, 'w') as outputFile:
    json.dump(outputValues, outputFile, sort_keys=True)
  print("Generated " + outputSummaryPath)

# Parses inputProfilePath into keys and values, and returns a dict whose keys match interestingKeys
def parse(inputProfilePath, interestingKeys):
  with open(inputProfilePath) as inputProfile:
    values = dict()
    currentKey = None
    for line in inputProfile.readlines():
      line = line.strip()
      lineText = line.replace("<td>", "").replace('<td class="numeric">', "").replace("</td>", "")
      if currentKey is not None:
        values[currentKey] = parseDuration(lineText)
      if lineText in interestingKeys:
        currentKey = lineText
      else:
        currentKey = None
    return values

# Given a duration such as 1h20m02.5s, returns a number like ((1*60)+20)*60+2=4802.5
def parseDuration(durationText):
  originalDurationText = durationText
  secondsText = "0"
  minutesText = "0"
  hoursText = "0"
  daysText = "0"
  if "d" in durationText:
   daysText, durationText = durationText.split("d")
  if "h" in durationText:
    hoursText, durationText = durationText.split("h")
  if "m" in durationText:
    minutesText, durationText = durationText.split("m")
  if "s" in durationText:
    secondsText, durationText = durationText.split("s")
  if durationText != "":
    raise Exception("Failed to parse '" + durationText + "'")
  try:
    return (((float(daysText) * 24 + float(hoursText)) * 60) + float(minutesText)) * 60 + float(secondsText)
  except ValueError as e:
    raise ValueError("Failed to parse '" + durationText + "'")

if __name__ == "__main__":
  main()
