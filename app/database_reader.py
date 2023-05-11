from app.models import User, Team, UploadFile, Game, Bet, UserTournaments, GamesPlayed, BetGroup, UserBetGroup
from app.my_error import TeamsDatabaseEmpty, GameNotExist, DatabaseReaderProblem, GamesDatabaseEmpty, BetsDatabaseEmpty


class TeamReader:

    def get_all_teams():
        teams = Team.query.all()
        if teams is None:
            raise TeamsDatabaseEmpty()
        else:
            return teams

    def get_one_team_by_filter(filter_name, filter):
        filter_name = None
        match filter_name:
            case "name":
                team = Team.query.filter_by(name=filter).first()
            case _:
                team = None
        if team is None:
            raise DatabaseReaderProblem()
        else:
            return team

    def get_sort_group(group_name):
        sorted_group = Team.query.filter_by(
            group=group_name).order_by(Team.points.desc(), Team.goal_balance.desc()).all()
        if sorted_group is None:
            raise DatabaseReaderProblem()
        else:
            return sorted_group


class GameReader:

    def get_all_games():
        games = Game.query.all()
        if games is None:
            raise GamesDatabaseEmpty()
        else:
            return games

    def get_count_games():
        games = Game.query.count()
        if games is None:
            raise GamesDatabaseEmpty()
        else:
            return games

    def get_all_games_filter(filter_name, filter):
        match filter_name:
            case "game_phase":
                game = Game.query.filter_by(game_phase=filter).all()
            case _:
                game = None
        if game is None:
            raise GameNotExist()
        else:
            return game

    def get_one_game_filter(filter_name, filter):
        match filter_name:
            case "id":
                game = Game.query.filter_by(id=filter).first()
            case _:
                game = None
        if game is None:
            raise GameNotExist()
        else:
            return game

    def get_all_games_by_day_order(day):
        games = Game.query.filter_by(
            game_day=day).order_by(Game.game_time.asc()).all()
        if games is None:
            raise DatabaseReaderProblem()
        else:
            return games

    def get_games_by_day_count(day):
        games = Game.query.filter_by(game_day=day).count()
        if games is None:
            raise DatabaseReaderProblem()
        else:
            return games

    def get_one_game_filter_order_asc(filter_name, filter):
        match filter_name:
            case "game_day":
                game = Game.query.filter_by(game_day=filter).order_by(
                    Game.game_time.asc()).first()
            case _:
                game = None
        if game is None:
            raise DatabaseReaderProblem()
        else:
            return game

    def get_one_game_filter_order_desc(filter_name, filter):
        match filter_name:
            case "game_day":
                game = Game.query.filter_by(game_day=filter).order_by(
                    Game.game_time.desc()).first()
            case _:
                game = None
        if game is None:
            raise DatabaseReaderProblem()
        else:
            return game


class UserReader:

    def get_one_user_filter(filter_name, filter):
        match filter_name:
            case "id":
                user = User.query.filter_by(id=filter).first()
            case "email":
                user = User.query.filter_by(email=filter).first()
            case "nick":
                user = User.query.filter_by(nick=filter).first()
            case _:
                user = None

        if user is None:
            raise DatabaseReaderProblem()
        else:
            return user


class TournamentReader:

    def get_all_tournaments_filter(filter_name, filter):
        match filter_name:
            case "user_id":
                tournaments = UserTournaments.query.filter_by(
                    user_id=filter).all()
            case _:
                tournaments = None

        if tournaments is None:
            raise DatabaseReaderProblem()
        else:
            return tournaments


class BetReader:

    def get_all_bets():
        bets = Bet.query.all()
        if bets is None:
            raise BetsDatabaseEmpty()
        else:
            return bets

    def get_all_bets_filter(filter_name, filter):
        match filter_name:
            case "user_id":
                bets = Bet.query.filter_by(user_id=filter).all()
            case "game_id":
                bets = Bet.query.filter_by(game_id=filter).all()
            case _:
                bets = None

        if bets is None:
            raise DatabaseReaderProblem()
        else:
            return bets

    def get_count_bets_filter(filter_name, filter):
        match filter_name:
            case "user_id":
                bets = Bet.query.filter_by(user_id=filter).count()
            case _:
                bets = None

        if bets is None:
            raise DatabaseReaderProblem()
        else:
            return bets

    def get_one_bet_filter(filter_name, filter):
        match filter_name:
            case "id":
                bet = Bet.query.filter_by(id=filter).first()
            case _:
                bet = None

        if bet is None:
            raise DatabaseReaderProblem()
        else:
            return bet


class BetGroupReader:

    def get_one_bet_group_filter(filter_name, filter):
        match filter_name:
            case "name":
                existing_group = BetGroup.query.filter_by(
                    name=filter).first()
            case "id":
                existing_group = BetGroup.query.filter_by(
                    id=filter).first()
            case _:
                existing_group = None

        if existing_group is None:
            raise DatabaseReaderProblem()
        else:
            return existing_group


class UserBetGroupReader:

    def get_all_user_groups_filter(filter_name, filter):
        match filter_name:
            case "user_id":
                user_groups = UserBetGroup.query.filter_by(
                    user_id=filter).all()
            case _:
                user_groups = None

        if user_groups is None:
            raise DatabaseReaderProblem()
        else:
            return user_groups

    def get_count_user_group_filter(filter_name, filter):
        match filter_name:
            case "user_id":
                user_bets = UserBetGroup.query.filter_by(
                    user_id=filter).count()
            case _:
                user_bets = None

        if user_bets is None:
            raise DatabaseReaderProblem()
        else:
            return user_bets

    def get_all_user_group_filter_order(filter_name, filter):
        match filter_name:
            case "bet_group_id":
                user_groups = UserBetGroup.query.filter_by(
                    bet_group_id=filter).order_by(UserBetGroup.points.desc()).all()
            case _:
                user_groups = None

        if user_groups is None:
            raise DatabaseReaderProblem()
        else:
            return user_groups


class FilesReader:

    def get_all_files():
        files = UploadFile.query.all()
        if files is None:
            raise DatabaseReaderProblem()
        else:
            return files

    def get_file_by_filter(file_idx):
        file = UploadFile.query.filter_by(id=file_idx).first()
        if file is None:
            raise DatabaseReaderProblem()
        else:
            return file


class GamesPlayedReader:

    def get_all_games_played():
        games_played = GamesPlayed.query.all()
        if games_played is None:
            raise GamesDatabaseEmpty()
        else:
            return games_played
