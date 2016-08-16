from venues.models import AdjudicatorVenueConstraint, InstitutionVenueConstraint, TeamVenueConstraint


def _constraints_satisfied(constraints_dict, key, venue):
    constraints = constraints_dict.get(key, [])
    return any(constraint.venue_group_id == venue.group_id for constraint in constraints)

def venue_conflicts_display(debates):
    """Returns a dict mapping elements (debates) in `debates` to a list of
    strings of explaning unfulfilled venue constraints for participants that
    debate. A venue constraint (or more precisely, a set of venue constraints
    relating to a single participant) is "unfulfilled" if the relevant
    participant had constraints and *none* of their constraints were met."""

    teamconstraints = {}
    for constraint in TeamVenueConstraint.objects.filter(team__debateteam__debate__in=debates).distinct():
        teamconstraints.setdefault(constraint.team_id, []).append(constraint)
    instconstraints = {}
    for constraint in InstitutionVenueConstraint.objects.filter(institution__team__debateteam__debate__in=debates).distinct():
        instconstraints.setdefault(constraint.institution_id, []).append(constraint)
    adjconstraints = {}
    for constraint in AdjudicatorVenueConstraint.objects.filter(adjudicator__debateadjudicator__debate__in=debates).distinct():
        adjconstraints.setdefault(constraint.adjudicator_id, []).append(constraint)

    conflict_messages = {debate: [] for debate in debates}
    for debate in debates:
        venue = debate.venue
        for team in debate.teams:
            if not _constraints_satisfied(teamconstraints, team.id, venue):
                conflict_messages[debate].append("Venue does not meet constraints of team {}".format(team.short_name))
            if not _constraints_satisfied(instconstraints, team.institution_id, venue):
                conflict_messages[debate].append("Venue does not meet constraints of institution {} ({})".format(team.institution.code, team.short_name))

        for adjudicator in debate.adjudicators.all():
            if not _constraints_satisfied(adjconstraints, adjudicator.id, venue):
                conflict_messages[debate].append("Venue does not meet constraints of adjudicator {}".format(adjudicator.name))

    return conflict_messages
