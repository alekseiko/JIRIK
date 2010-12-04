#!/usr/bin/env python

__author__ = "aleksei.kornev@gmail.com (Aleksei Kornev)"

import SOAPpy
import time
from optparse import OptionParser

import config

TIME_FORMAT = "%d%m%Y"
ISSUE_BY_PART_OF_NAME_JQL = "project = {0} AND summary ~ '{1}'" 
START_DATE_FIELD = "startDate"
TIME_SPENT_FIELD = "timeSpent"
COMMENT_FIELD = "comment"

class JiraEngine: 

	def __init__(self, login, password, url):
		self.__login = login
		self.__password = password
		self.__url = url
	
	def addWorklogAndAutoAdjustRemainingEstimate(self, issue, createDate, \
				timeSpent, comment):

		client, auth = self.__initJiraClient()

		dt_today = SOAPpy.dateTimeType(createDate)
		worklog = {START_DATE_FIELD:dt_today, \
				TIME_SPENT_FIELD:timeSpent, \
				COMMENT_FIELD:comment}

		result = client.addWorklogAndAutoAdjustRemainingEstimate(auth, \
				issue, worklog)
		
	def getIssuesByPartOfName(self, partOfName, project = config.project, \
				resultCount = config.resultCount):

		client, auth = self.__initJiraClient()

		return [(issue["key"], issue["summary"]) \
			for issue in client.getIssuesFromJqlSearch(auth, \
			ISSUE_BY_PART_OF_NAME_JQL.format(project, \
			partOfName), resultCount)]

	def __initJiraClient(self):
		client = SOAPpy.SOAPProxy(self.__url)
		auth = client.login(self.__login, self.__password)
		return client, auth		

def main():
	options = parseArgs()
	
	jira = JiraEngine(config.jiraLogin, config.jiraPassword, \
				config.jiraEndpoint) 

	issues = None
	if options.project is None:
		issues = jira.getIssuesByPartOfName(options.summary)
	else:
		issues = jira.getIssuesByPartOfName(options.summary, \
				options.project)

#	If we found more then 1 issue we need to choose right issue
	number = 0
	if len(issues) > 1:
		while(True):
			for index, (key, summary) in enumerate(issues):
				print "({0}) [{1}] {2}".format(index, key, \
					summary)
			value = raw_input("Choose issue or x for exit: ")

			if (value == 'x'): 
				return

			try:
				value = int(value)
			except ValueError:
				print "We can type 'x' or number of row\n"
				continue

			if ((value < len(issues)) and (value >= 0)):
				number = value
				break

			print "Wrong number. Please choose again."	

	elif (len(issues) == 0):
		print "Issue didn't find"
		return

	(issueKey, summary) = issues[number]
	jira.addWorklogAndAutoAdjustRemainingEstimate(issueKey, \
			time.strptime(options.date, TIME_FORMAT)[:6], \
			options.timeSpent, options.comment)

	print "Worklog is successfully logged on issue: [{0}]".format(issueKey)

def parseArgs():
	parser = OptionParser()
	parser.add_option("-t", "--time", dest = TIME_SPENT_FIELD,\
		help = "timeSpent on issue in jira format 1h, 1d, etc", \
		type = "string")
	parser.add_option("-s", "--summary",\
		help = "Part of summary", dest = "summary", type = "string")
	parser.add_option("-d", "--date",\
		help = "Start date in format ddmmYYYY", dest = "date", \
		type = "string")
	parser.add_option("-c", "--comment", \
		help = "Comment for work log", dest = COMMENT_FIELD, \
		type = "string")
	parser.add_option("-p", "--project",\
		help = "Project name", dest = "project", type = "string")
	(options, args) = parser.parse_args()
	
	return options
		


if __name__ == "__main__":
	main()	
