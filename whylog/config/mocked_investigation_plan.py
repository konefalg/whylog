from datetime import datetime

from whylog.config.filename_matchers import WildCardFilenameMatcher
from whylog.config.investigation_plan import Clue, InvestigationPlan, InvestigationStep, LineSource
from whylog.config.log_type import LogType
from whylog.config.parser_subset import ConcatenatedRegexParser
from whylog.config.parsers import RegexParser
from whylog.config.rule import Rule
from whylog.config.super_parser import RegexSuperParser


# mocked investigation plan for 003_match_time_range test
# TODO: remove mock
def mocked_investigation_plan():
    super_parser = RegexSuperParser('^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d).*', [1], {1: 'date'})
    matcher = WildCardFilenameMatcher('localhost', 'node_1.log', 'default', super_parser)
    default_log_type = LogType('default', [matcher])
    cause = RegexParser(
        'cause', '2015-12-03 12:08:08 root cause',
        '^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) root cause$', [1], 'default', {1: 'date'}
    )
    effect = RegexParser(
        'effect', '2015-12-03 12:08:09 visible effect',
        '^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) visible effect$', [1], 'default', {1: 'date'}
    )
    concatenated = ConcatenatedRegexParser([cause])
    effect_time = datetime(2015, 12, 3, 12, 8, 9)
    search_range = {
        'default': {
            'date': {
                'left_bound': datetime(2015, 12, 3, 12, 8, 8),
                'right_bound': effect_time
            }
        }
    }
    default_investigation_step = InvestigationStep(concatenated, search_range)
    rule = Rule(
        [cause], effect, [
            {
                'clues_groups': [[1, 1], [0, 1]],
                'name': 'time',
                'params': {'max_delta': 1}
            }
        ], Rule.LINKAGE_AND
    )  # yapf: disable
    line_source = LineSource('localhost', 'node_1.log')
    effect_clues = {'effect': Clue((effect_time,), 'visible effect', 40, line_source)}
    return InvestigationPlan([rule], [(default_investigation_step, default_log_type)], effect_clues)
