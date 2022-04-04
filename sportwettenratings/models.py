from django.db import models


class Country(models.Model):
    name = models.CharField(unique=True, max_length=64)
    alt_name = models.CharField(max_length=64, null=True)
    code2 = models.CharField(max_length=16, null=True)
    code3 = models.CharField(max_length=16, null=True)
    flag = models.CharField(max_length=256, null=True)
    slug = models.SlugField(unique=True, max_length=64)

    class Meta:
        ordering = ['name']


class League(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64)
    type = models.CharField(max_length=16)
    logo = models.CharField(max_length=256, null=True)
    code = models.CharField(max_length=16, null=True)
    country = models.ForeignKey(to='Country', on_delete=models.CASCADE)
    slug = models.SlugField(max_length=64)

    class Meta:
        ordering = ['country', 'name']


class Season(models.Model):
    year = models.IntegerField()
    start = models.DateField()
    end = models.DateField()
    current = models.BooleanField()
    league = models.ForeignKey(to='League', on_delete=models.CASCADE)
    logo = models.CharField(max_length=256, null=True)
    slug = models.SlugField(max_length=64)
    last_updated = models.DateField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['year', 'league'], name='unique_season')
        ]
        ordering = ['league', '-year']


class Team(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64)
    country = models.ForeignKey(to='Country', on_delete=models.CASCADE)
    logo = models.CharField(max_length=256, null=True)
    national = models.BooleanField()
    code = models.CharField(max_length=16, null=True)
    slug = models.SlugField(max_length=64)

    class Meta:
        ordering = ['name']


class TeamToSeason(models.Model):
    season = models.ForeignKey(to='Season', on_delete=models.CASCADE)
    team = models.ForeignKey(to='Team', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['season', 'team'], name='unique_team_to_season')
        ]
        ordering = ['team', '-season']


class Fixture(models.Model):
    id = models.IntegerField(primary_key=True)
    date = models.DateTimeField()
    status_long = models.CharField(max_length=32)
    status_short = models.CharField(max_length=16)
    season = models.ForeignKey(to='Season', on_delete=models.CASCADE)
    round = models.CharField(max_length=64)
    hometeam = models.ForeignKey(to='TeamToSeason', on_delete=models.CASCADE, related_name='hometeam')
    awayteam = models.ForeignKey(to='TeamToSeason', on_delete=models.CASCADE, related_name='awayteam')
    homescore_ht = models.IntegerField(null=True)
    awayscore_ht = models.IntegerField(null=True)
    homescore_ft = models.IntegerField(null=True)
    awayscore_ft = models.IntegerField(null=True)
    homescore_et = models.IntegerField(null=True)
    awayscore_et = models.IntegerField(null=True)
    homescore_p = models.IntegerField(null=True)
    awayscore_p = models.IntegerField(null=True)
    slug = models.SlugField(unique=True, max_length=128)

    class Meta:
        ordering = ['season', 'date']


class Statistic(models.Model):
    id = models.OneToOneField(to='Fixture', on_delete=models.CASCADE, primary_key=True, db_column='id')
    shots_on_goal_h = models.IntegerField(null=True)
    shots_on_goal_a = models.IntegerField(null=True)
    shots_off_goal_h = models.IntegerField(null=True)
    shots_off_goal_a = models.IntegerField(null=True)
    total_shots_h = models.IntegerField(null=True)
    total_shots_a = models.IntegerField(null=True)
    blocked_shots_h = models.IntegerField(null=True)
    blocked_shots_a = models.IntegerField(null=True)
    shots_insidebox_h = models.IntegerField(null=True)
    shots_insidebox_a = models.IntegerField(null=True)
    shots_outsidebox_h = models.IntegerField(null=True)
    shots_outsidebox_a = models.IntegerField(null=True)
    fouls_h = models.IntegerField(null=True)
    fouls_a = models.IntegerField(null=True)
    corner_kicks_h = models.IntegerField(null=True)
    corner_kicks_a = models.IntegerField(null=True)
    offsides_h = models.IntegerField(null=True)
    offsides_a = models.IntegerField(null=True)
    ball_possession_h = models.FloatField(null=True)
    ball_possession_a = models.FloatField(null=True)
    yellow_cards_h = models.IntegerField(null=True)
    yellow_cards_a = models.IntegerField(null=True)
    red_cards_h = models.IntegerField(null=True)
    red_cards_a = models.IntegerField(null=True)
    goalkeeper_saves_h = models.IntegerField(null=True)
    goalkeeper_saves_a = models.IntegerField(null=True)
    total_passes_h = models.IntegerField(null=True)
    total_passes_a = models.IntegerField(null=True)
    passes_accurate_h = models.IntegerField(null=True)
    passes_accurate_a = models.IntegerField(null=True)
    passes_percent_h = models.FloatField(null=True)
    passes_percent_a = models.FloatField(null=True)
    cross_attacks_h = models.IntegerField(null=True)
    cross_attacks_a = models.IntegerField(null=True)
    assists_h = models.IntegerField(null=True)
    assists_a = models.IntegerField(null=True)
    counter_attacks_h = models.IntegerField(null=True)
    counter_attacks_a = models.IntegerField(null=True)
    substitutions_h = models.IntegerField(null=True)
    substitutions_a = models.IntegerField(null=True)

    class Meta:
        ordering = ['id']


class Bookmaker(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64)

    class Meta:
        ordering = ['name']


class Bet(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64)

    class Meta:
        ordering = ['name']


class Odd(models.Model):
    match = models.ForeignKey(to='Fixture', on_delete=models.CASCADE)
    bookmaker = models.ForeignKey(to='Bookmaker', on_delete=models.CASCADE)
    bet = models.ForeignKey(to='Bet', on_delete=models.CASCADE)
    value = models.CharField(max_length=256)
    odd = models.FloatField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['match', 'bookmaker', 'bet', 'value'], name='unique_odd')
        ]
        ordering = ['match', 'bet', 'bookmaker']


class Player(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64)
    firstname = models.CharField(max_length=64)
    lastname = models.CharField(max_length=64)
    age = models.IntegerField()
    birth_date = models.DateField()
    birth_place = models.CharField(max_length=64, null=True)
    birth_country = models.CharField(max_length=64)
    nationality = models.CharField(max_length=64)
    height = models.IntegerField()
    weight = models.IntegerField()
    injured = models.BooleanField()
    photo = models.CharField(max_length=256, null=True)
    slug = models.SlugField(max_length=64)


class Event(models.Model):
    time_elapsed = models.IntegerField()
    time_extra = models.IntegerField(null=True)
    team = models.ForeignKey(to='TeamToSeason', on_delete=models.CASCADE)
    player = models.ForeignKey(to='Player', on_delete=models.CASCADE, related_name='player')
    assist = models.ForeignKey(to='Player', on_delete=models.CASCADE, related_name='assist', null=True)
    type = models.CharField(max_length=32)
    detail = models.CharField(max_length=32)
    comments = models.CharField(max_length=64, null=True)


class PlayerTeamSeason(models.Model):
    player = models.ForeignKey(to='Player', on_delete=models.CASCADE)
    team = models.ForeignKey(to='TeamToSeason', on_delete=models.CASCADE)


'''class PlayerStatistics(models.Model):
    pass


class Transfer(models.Model):
    pass


class Coach(models.Model):
    pass


class Squad(models.Model):
    pass


class Trophy(models.Model):
    pass


class Sidelined(models.Model):
    pass


class Venue(models.Model):
    pass


class Rating(models.Model):
    pass


class Prediction(models.Model):
    pass'''
