# coding=utf-8
import sys
import os
import time
from django.utils import timezone
import django
# pip install pypinyin
# https://github.com/mozillazg/python-pinyin
from pypinyin import pinyin, Style
# pip install Pillow
from PIL import Image


sys.path.append('../')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "oj.settings")
django.setup()

try:
    from account.models import *
    # from group.models import *
    from submission.models import *
    from contest.models import *
    # from judge.result import *
    from oj.settings import *
except ImportError:
    exit(1)

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


cdp_path = os.path.join(os.getcwd(), 'cdp')
images_path = os.path.join(cdp_path, 'images')
logo_path = os.path.join(images_path, 'logo')
team_path = os.path.join(images_path, 'team')


image_file_dir = os.path.join(BASE_DIR, "upload")


if not os.path.exists(cdp_path):
    os.mkdir(cdp_path)

if not os.path.exists(images_path):
    os.mkdir(images_path)

if not os.path.exists(logo_path):
    os.mkdir(logo_path)

if not os.path.exists(team_path):
    os.mkdir(team_path)

outfile = open(os.path.join(cdp_path, 'generate.xml'), 'wb')
root = ET.Element('contest')

school_names = ['School of Computer and Communication Engineering',
                'School of Automation and Electrical Engineering',
                'School of Advanced Engineering',
                'School of Mathematics and Physics',
                'Donlinks School of Economics and Management',
                'School of Civil and Resources Engineering',
                ]

languages = [
    {'id': 1, 'name': 'c'},
    {'id': 2, 'name': 'c++'},
    {'id': 3, 'name': 'java'},
]

judgements = [
    {'id': 1, 'acronym': 'AC', 'name': 'Yes', 'solved': 'true', 'penalty': 'false'},
    {'id': 2, 'acronym': 'WA', 'name': 'No - Wrong Answer', 'solved': 'false', 'penalty': 'true'},
    {'id': 3, 'acronym': 'CE', 'name': 'No - Compile Error', 'solved': 'false', 'penalty': 'true'},
    {'id': 4, 'acronym': 'RE', 'name': 'No - Run Time Error', 'solved': 'false', 'penalty': 'true'},
    {'id': 5, 'acronym': 'SE', 'name': 'No - System Error', 'solved': 'false', 'penalty': 'false'},
]

judge_state_mapping = {
    JudgeStatus.COMPILE_ERROR: 3,
    JudgeStatus.WRONG_ANSWER: 2,
    JudgeStatus.ACCEPTED: 1,
    JudgeStatus.CPU_TIME_LIMIT_EXCEEDED: 2,
    JudgeStatus.REAL_TIME_LIMIT_EXCEEDED: 2,
    JudgeStatus.MEMORY_LIMIT_EXCEEDED: 2,
    JudgeStatus.RUNTIME_ERROR: 4,
    JudgeStatus.SYSTEM_ERROR: 5,
}


def add_info(contest, title_en):
    info = ET.SubElement(root, 'info')

    length = ET.SubElement(info, 'length')
    length.text = str(contest.end_time - contest.start_time)

    penalty = ET.SubElement(info, 'penalty')
    penalty.text = '20'

    started = ET.SubElement(info, 'started')
    started.text = 'False'

    starttime = ET.SubElement(info, 'starttime')
    starttime.text = str(time.mktime(timezone.localtime(contest.start_time).timetuple()))

    title = ET.SubElement(info, 'title')
    title.text = title_en

    short_title = ET.SubElement(info, 'short-title')
    short_title.text = title_en

    scc = ET.SubElement(info, 'scoreboard-freeze-length')
    scc.text = "0:30:00"

    contest_id = ET.SubElement(info, 'contest-id')
    contest_id.text = 'default--' + str(contest.id)


def add_region():
    idx = 1
    for school in school_names:
        region = ET.SubElement(root, 'region')

        external_id = ET.SubElement(region, 'external-id')
        external_id.text = str(idx)

        name = ET.SubElement(region, 'name')
        name.text = school

        idx += 1


def add_judgement():
    for item in judgements:
        judgement = ET.SubElement(root, 'judgement')

        ids = ET.SubElement(judgement, 'id')
        ids.text = str(item['id'])

        acronym = ET.SubElement(judgement, 'acronym')
        acronym.text = item['acronym']

        name = ET.SubElement(judgement, 'name')
        name.text = item['name']

        solved = ET.SubElement(judgement, 'solved')
        solved.text = item['solved']

        penalty = ET.SubElement(judgement, 'penalty')
        penalty.text = item['penalty']


def add_language():
    for item in languages:
        language = ET.SubElement(root, 'language')
        ids = ET.SubElement(language, 'id')
        ids.text = str(item['id'])

        name = ET.SubElement(language, 'name')
        name.text = item['name']


def add_problems(contest):
    contest_problems = Problem.objects.filter(contest=contest, visible=True).order_by("_id")
    problem_id_map = {}
    idx = 1
    for problem_object in contest_problems:
        problem = ET.SubElement(root, 'problem')

        ids = ET.SubElement(problem, 'id')
        problem_id_map[problem_object.id] = idx
        ids.text = str(idx)
        idx += 1

        letter = ET.SubElement(problem, '_id')
        letter.text = problem_object._id

        name = ET.SubElement(problem, 'name')
        name.text = problem_object.title

    print('add problems done!')
    return problem_id_map


def get_english_name(cn_name):
    star = cn_name[0] == u'*'
    if star:
        cn_name = cn_name[1:]
    pin = pinyin(cn_name, style=Style.NORMAL)
    data = []
    for sub in pin:
        data.append(sub[0])
    if len(data) == 3:
        english_name = str(data[1] + data[2]).capitalize() + " " + str(data[0]).capitalize()
    else:
        english_name = str(data[1]).capitalize() + " " + str(data[0]).capitalize()
    return "* " + english_name if star else english_name


def add_team(user_object):
    team = ET.SubElement(root, 'team')

    ids = ET.SubElement(team, 'id')
    ids.text = str(user_object.id)

    external_id = ET.SubElement(team, 'external-id')
    external_id.text = str(user_object.id)

    # school_id = 1
    # if u'自动化学院' in user_object.userprofile.school:
    #     school_id = 2
    # elif u'高等工程师学院' in user_object.userprofile.school:
    #     school_id = 3
    # elif u'数理学院' in user_object.userprofile.school:
    #     school_id = 4
    # elif u'东凌经济管理学院' in user_object.userprofile.school:
    #     school_id = 5
    # elif u'土木与资源工程学院' in user_object.userprofile.school:
    #     school_id = 6

    region = ET.SubElement(team, 'region')
    # region.text = school_names[school_id - 1]
    region.text = user_object.userprofile.school

    name = ET.SubElement(team, 'name')
    # name.text = get_english_name(user_object.userprofile.real_name)
    name.text = user_object.userprofile.real_name

    university = ET.SubElement(team, 'university')
    # university.text = get_english_name(user_object.userprofile.real_name)
    university.text = user_object.userprofile.real_name

    aim_avatar_path = os.path.join(logo_path, str(user_object.id) + '.png')
    user_avatar_path = DATA_DIR + user_object.userprofile.avatar
    user_avatar = Image.open(user_avatar_path)
    user_avatar.save(aim_avatar_path)


def add_runs(contest, problem_id_map):
    submissions = Submission.objects.filter(contest_id=contest.id).order_by("create_time")
    submissions = submissions.filter(create_time__gte=contest.start_time)

    id_index = 1
    for item in submissions:
        run = ET.SubElement(root, 'run')

        idx = ET.SubElement(run, 'id')
        idx.text = str(id_index)
        id_index += 1

        judged = ET.SubElement(run, 'judged')
        judged.text = 'True'

        language = ET.SubElement(run, 'language')
        # language.text = languages[item.language - 1]['name']
        language.text = item.language

        problem = ET.SubElement(run, 'problem')
        problem.text = str(problem_id_map[item.problem_id])

        status = ET.SubElement(run, 'status')
        status.text = 'done'

        team = ET.SubElement(run, 'team')
        team.text = str(item.user_id)

        times = ET.SubElement(run, 'time')
        times.text = str((item.create_time - contest.start_time).total_seconds())

        timestamp = ET.SubElement(run, 'timestamp')
        timestamp.text = str(time.mktime(timezone.localtime(item.create_time).timetuple())
                             + item.create_time.microsecond / 1e6)

        solved = ET.SubElement(run, 'solved')
        penalty = ET.SubElement(run, 'penalty')
        results = ET.SubElement(run, 'result')

        assert(item.result != JudgeStatus.PENDING)
        assert(item.result != JudgeStatus.JUDGING)
        assert(item.result != JudgeStatus.PARTIALLY_ACCEPTED)
        judgement = judgements[judge_state_mapping[item.result]]

        solved.text = judgement['solved']
        penalty.text = judgement['penalty']
        results.text = judgement['acronym']

    print('add contest run done!')


def add_award(team_id, typ, citation):
    award = ET.SubElement(root, 'award')
    ET.SubElement(award, 'team').text = str(team_id)
    ET.SubElement(award, 'type').text = str(typ)
    ET.SubElement(award, 'citation').text = str(citation)


def add_medal(contest):
    rank =  ACMContestRank.objects.filter(contest_id=contest.id). \
            select_related("user"). \
            order_by("-accepted_number", "total_time"). \
            values("id", "user__id", "user__username", "user__userprofile__real_name",
                   "user__userprofile__avatar",
                   "contest_id", "submission_info", "submission_number", "accepted_number", "total_time")

    gold = int(input("input gold numbers:").strip())
    silver = int(input("input silver numbers:").strip())
    bronze = int(input("input bronze numbers:").strip())

    silver += gold
    bronze += silver

    rank_number = 1
    rank_number_without_star = 1

    last_gold = last_silver = last_bronze = len(rank)

    for item in rank:
        # 只有有ac的题目而且不是打星的队伍才参与排名
        if item["accepted_number"] == 0:
            break

        if rank_number_without_star == gold:
            last_gold = rank_number
        elif rank_number_without_star == silver:
            last_silver = rank_number
        elif rank_number_without_star == bronze:
            last_bronze = rank_number
        rank_number += 1

        if item["user__userprofile__real_name"][0] != "*":
            if rank_number_without_star <= gold:
                add_award(item['user__id'], 'medal', 'Gold Medalist')
            elif rank_number_without_star <= silver:
                add_award(item['user__id'], 'medal', 'Silver Medalist')
            elif rank_number_without_star <= bronze:
                add_award(item['user__id'], 'medal', 'Bronze Medalist')
            else:
                break
            rank_number_without_star += 1

    print('add medal done!')
    return last_gold, last_silver, last_bronze


def add_finalized(contest):
    finalized = ET.SubElement(root, 'finalized')
    last_gold, last_silver, last_bronze = add_medal(contest)

    ET.SubElement(finalized, 'last_gold').text = str(last_gold)
    ET.SubElement(finalized, 'last_silver').text = str(last_silver)
    ET.SubElement(finalized, 'last_bronze').text = str(last_bronze)

    ET.SubElement(finalized, 'time').text = '0'
    ET.SubElement(finalized, 'timestamp').text = \
        str(time.mktime(timezone.localtime(contest.end_time).timetuple()) + contest.end_time.microsecond / 1e6)

    print('add finalized done!')


def export():
    try:
        contests = Contest.objects.all()
        print('contest list:')
        for contest in contests:
            print("%s: %s" % (contest.id, contest.title))
        cid = input('please choose contest:').strip()
        cid = int(cid)
        contest = Contest.objects.get(id=cid)
        title = input('please input contest title without zh-cn:').strip()

        add_info(contest, title)
        print('add info done!')

        add_region()
        print('add region done!')

        add_judgement()
        print('add judgement done!')

        add_language()
        print('add language done!')

        user_id_list = Submission.objects.filter(contest=contest).order_by('user_id') \
                                         .distinct('user_id').values_list('user_id', flat=True)
        user_related = User.objects.filter(id__in=user_id_list).filter(admin_type=AdminType.REGULAR_USER)
        for item in user_related:
            add_team(item)
        print('add team done!')

        problem_id_map = add_problems(contest)
        add_runs(contest, problem_id_map)

        add_finalized(contest)

    except Exception as e:
        print(e)
        return False

    return True


if __name__ == '__main__':
    # add_info(Contest.objects.get(id=1), 'hello world')
    # add_region()
    # add_judgement()
    # add_language()
    # add_problem(ContestProblem.objects.get(id=2))
    # add_team(User.objects.get(id=1))
    if export():
        root = ET.ElementTree(root)
        root.write(outfile)
        print('success!')