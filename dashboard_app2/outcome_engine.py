import pandas as pd


def _safe_market_value(value) -> float:
    if pd.isna(value):
        return 0
    return float(value)


def _days_between(start, end) -> float:
    if pd.isna(start) or pd.isna(end):
        return 0
    return max((end - start).days, 0)


def _is_true(value) -> bool:
    return bool(value) if pd.notna(value) else False


def _score_change(start_score, next_score):
    if pd.isna(start_score) or pd.isna(next_score):
        return None
    return float(next_score) - float(start_score)


def _build_outcome_label(row) -> str:
    labels = []

    if pd.isna(row["next_league_quality_change"]):
        labels.append("no next league comparison")
    elif row["moved_up"]:
        labels.append("moved up")
    elif row["moved_down"]:
        labels.append("moved down")
    else:
        labels.append("stayed level")

    if row["market_value_increased"]:
        labels.append("market value increased")

    if row["returned_home"]:
        labels.append("returned home")
    elif row["became_international"]:
        labels.append("international path")

    if row["became_free_agent"]:
        labels.append("became free agent")

    if row["retired_or_inactive"]:
        labels.append("retired / inactive")

    return ", ".join(labels)


def get_career_outcomes(master: pd.DataFrame,
                        cohort: pd.DataFrame) -> pd.DataFrame:
    """
    Reconstructs each player's career AFTER the selected transfer.

    Parameters
    ----------
    master : complete transfer history

    cohort : transfers currently selected in the dashboard

    Returns
    -------
    One row per selected transfer with summary information
    about everything that happened afterwards.
    """

    master = master.copy()
    master["date"] = pd.to_datetime(master["date"], utc=True)
    cohort = cohort.copy()
    cohort["date"] = pd.to_datetime(cohort["date"], utc=True)
    today = pd.Timestamp.now(tz="UTC")

    # Sort complete career history
    history = master.sort_values(
        ["player_id", "date"]
    ).copy()

    outcomes = []

    for _, transfer in cohort.iterrows():

        player = transfer["player_id"]

        transfer_date = transfer["date"]
        start_country = transfer.get("from_country_name")
        destination_country = transfer.get("to_country_name")
        home_country = transfer.get("primary_nationality")
        start_value = _safe_market_value(transfer.get("market_value"))
        decision_league_quality_change = transfer.get(
            "league_quality_change", 0)
        if pd.isna(decision_league_quality_change):
            decision_league_quality_change = 0

        career = history[
            history["player_id"] == player
        ].sort_values("date")

        # Everything AFTER the selected transfer
        future = career[
            career["date"] > transfer_date
        ]

        ###################################################
        # No later transfer
        ###################################################

        if future.empty:

            last_transfer = transfer

            observed_days = _days_between(transfer_date, today)
            became_free_agent = bool(
                _is_true(transfer.get("to_free_agent", False))
                or transfer.get("to_league") == "Without a club"
                or transfer.get("to_club_name") == "Without a club"
            )

            outcomes.append({

                "player_id": player,
                "player_name": transfer["full_name"],
                "transfer_date": transfer_date,

                "future_transfers": 0,
                "next_transfer_date": None,
                "days_to_next_transfer": None,
                "years_until_next_transfer": None,
                "observed_days_after_decision": observed_days,
                "stayed_6_months": observed_days >= 183,
                "stayed_2_years": observed_days >= 730,
                "stayed_5_years": observed_days >= 1825,

                "decision_league_quality_change":
                decision_league_quality_change,
                "next_league_quality_change": None,
                "moved_up": False,
                "moved_down": False,
                "stayed_level": False,

                "next_league": None,
                "next_country": None,

                "last_league": last_transfer["to_league"],
                "last_country": last_transfer["to_country_name"],

                "returned_home": (
                    last_transfer["to_country_name"]
                    == home_country
                ),

                "ended_abroad": (
                    last_transfer["to_country_name"]
                    != home_country
                ),

                "became_international": (
                    destination_country != start_country
                    or last_transfer["to_country_name"] != start_country
                ),

                "became_free_agent": became_free_agent,
                "retired_or_inactive": (
                    became_free_agent
                    or observed_days >= 730
                ),

                "start_market_value": start_value,
                "final_market_value": last_transfer["market_value"],
                "market_value_change":
                    _safe_market_value(last_transfer["market_value"])
                    - start_value,
                "market_value_increased": (
                    _safe_market_value(last_transfer["market_value"])
                    > start_value
                ),
                "current_status": (
                    "No later transfer recorded"
                    if not became_free_agent
                    else "Free agent / without club"
                )

            })

            continue

        # ----------------------------------------
        # Player transferred again
        # ----------------------------------------

        next_transfer = future.iloc[0]
        last_transfer = future.iloc[-1]
        days_to_next = _days_between(transfer_date, next_transfer["date"])
        final_value = _safe_market_value(last_transfer.get("market_value"))
        next_league_quality_change = _score_change(
            transfer.get("to_score"),
            next_transfer.get("to_score"),
        )
        moved_up = (
            next_league_quality_change is not None
            and next_league_quality_change > 2
        )
        moved_down = (
            next_league_quality_change is not None
            and next_league_quality_change < -2
        )
        stayed_level = (
            next_league_quality_change is not None
            and abs(next_league_quality_change) <= 2
        )
        became_free_agent = bool(
            _is_true(transfer.get("to_free_agent", False))
            or future.get("to_free_agent", pd.Series(dtype=bool)).fillna(False).any()
            or (future.get("to_league", pd.Series(dtype=object)) == "Without a club").any()
            or (future.get("to_club_name", pd.Series(dtype=object)) == "Without a club").any()
        )

        outcomes.append({

            "player_id": player,
            "player_name": transfer["full_name"],
            "transfer_date": transfer_date,

            "future_transfers": len(future),
            "next_transfer_date": next_transfer["date"],
            "days_to_next_transfer": days_to_next,
            "years_until_next_transfer": days_to_next / 365.25,
            "observed_days_after_decision": _days_between(transfer_date, last_transfer["date"]),
            "stayed_6_months": days_to_next >= 183,
            "stayed_2_years": days_to_next >= 730,
            "stayed_5_years": days_to_next >= 1825,

            "next_league": next_transfer["to_league"],
            "next_country": next_transfer["to_country_name"],
            "decision_league_quality_change": decision_league_quality_change,
            "next_league_quality_change": next_league_quality_change,
            "moved_up": moved_up,
            "moved_down": moved_down,
            "stayed_level": stayed_level,

            "last_league": last_transfer["to_league"],
            "last_country": last_transfer["to_country_name"],

            "returned_home": (
                last_transfer["to_country_name"]
                == home_country
            ),

            "ended_abroad": (
                last_transfer["to_country_name"]
                != home_country
            ),

            "became_international": (
                destination_country != start_country
                or (future["to_country_name"] != start_country).any()
            ),

            "became_free_agent": became_free_agent,
            "retired_or_inactive": bool(
                became_free_agent
                and pd.isna(last_transfer.get("contract_until_y"))
            ),

            "start_market_value": start_value,
            "final_market_value": last_transfer["market_value"],
            "market_value_change": final_value - start_value,
            "market_value_increased": final_value > start_value,
            "current_status": "Transferred again"

        })

    outcome_frame = pd.DataFrame(outcomes)
    if not outcome_frame.empty:
        outcome_frame["outcome_summary"] = outcome_frame.apply(
            _build_outcome_label,
            axis=1,
        )

    return outcome_frame
