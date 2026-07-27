# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Kickways is for semi-professional and amateur football players who want to understand realistic international career moves. Agents and people close to player career planning are also relevant users when they need evidence for possible destinations.

Users usually arrive with one practical question: if I play here today, where could my career realistically go next?

## Product Purpose

Kickways helps football players and agents discover realistic career opportunities based on historical transfer patterns. It turns a player's current country, league, age, and profile context into a ranked set of destinations and destination intelligence.

Success means the user can move from current context to credible next destinations, understand why those destinations are realistic, and make a better shortlist decision.

## Positioning

Kickways is a Career Intelligence platform, not a football database. Its mechanism is historical transfer evidence: comparable players, observed destination paths, Opta league strength movement, and Transfermarkt-linked player examples.

The product should always answer the career-planning question rather than expose raw analytics or database functionality.

## Operating Context

The primary workflow is:

1. Input the player's current football context.
2. Review realistic career opportunities.
3. Inspect a destination.
4. Read career intelligence for that destination.
5. Decide whether the destination belongs on the player's shortlist.

The current implementation is a Streamlit web application. The intended production deployment context is Railway.

## Capabilities and Constraints

The app uses DuckDB-backed transfer data where possible. Historical transfer rows, player profiles, Transfermarkt profile links, and Opta league strength ratings are core product data.

Destination metrics must stay consistent between overview cards and destination intelligence pages. Level movement is defined by Opta league strength comparison:

- Level up: destination league has a higher Opta strength rating than the previous league.
- Same level: destination league has the same Opta strength rating as the previous league.
- Level down: destination league has a lower Opta strength rating than the previous league.

The product should not add unsupported claims, fabricated proof, invented testimonials, or unverified market conclusions.

## Brand Commitments

The product name is Kickways.

The tone should be clear, premium, decision-oriented, and practical. The app should feel like a SaaS career intelligence product rather than a database explorer or Streamlit demo.

## Evidence on Hand

Real evidence currently available in the project includes transfer history data, player profile data, Transfermarkt-derived profile links, Opta league strength mappings, and destination intelligence content.

Future work must not fabricate external proof, customer logos, testimonials, pricing claims, or deployment claims beyond the confirmed Railway target.

## Product Principles

Prioritize the user's career journey over feature inventory.

Every screen should answer what the user should do next.

Present historical evidence as decision intelligence, not raw database output.

Keep analytics available, but organize them around realistic career moves and destination shortlisting.

Preserve metric consistency across overview, drill-down, and destination report surfaces.

## Accessibility & Inclusion

The product should remain usable for players and agents who are not data experts. Copy, controls, and metrics should be plain-language and scannable.
