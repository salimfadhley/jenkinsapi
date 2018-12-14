"""
A selection of view objects used in testing.
"""

VIEW_WITH_FILTER_AND_REGEX = """
<?xml version="1.1" encoding="UTF-8"?>
<hudson.model.ListView>
  <name>%s</name>
  <filterExecutors>true</filterExecutors>
  <filterQueue>true</filterQueue>
  <properties class="hudson.model.View$PropertyList"/>
  <jobNames>
    <comparator class="hudson.util.CaseInsensitiveComparator"/>
  </jobNames>
  <jobFilters/>
  <columns>
    <hudson.views.StatusColumn/>
    <hudson.views.WeatherColumn/>
    <hudson.views.JobColumn/>
    <hudson.views.LastSuccessColumn/>
    <hudson.views.LastFailureColumn/>
    <hudson.views.LastDurationColumn/>
    <hudson.views.BuildButtonColumn/>
  </columns>
  <includeRegex>regex</includeRegex>
  <recurse>false</recurse>
</hudson.model.ListView>
""".strip()
