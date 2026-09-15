# TaskHub Public Demonstration Session Isolation

## Goal

Allow multiple people to try the publicly deployed TaskHub application without sharing visitor-entered profiles, groups, memberships, or tasks.

## Approved behavior

- Each Streamlit session receives one random 32-character lowercase hexadecimal identifier.
- The identifier is created by the application, stored in Streamlit session state, and never entered or displayed by a visitor.
- The storage layer validates the identifier before mapping it to `data/sessions/<identifier>.db`.
- Normal Streamlit reruns in the same active session reuse that database.
- A separate browser session uses a different database and begins without another session's content.
- All existing SQLite tables, validation, permissions, AI rules, dashboards, filters, cards, and calendar behavior remain unchanged.

## Privacy and persistence boundary

This feature isolates demonstration sessions; it does not authenticate people. A new browser session, expired session, app reboot, or Streamlit Community Cloud redeployment may start with empty data. Visitors must not enter personal, private, confidential, or sensitive information.

## Verification

- Unit tests prove distinct valid identifiers produce distinct paths.
- Unit tests reject malformed, non-hexadecimal, overlong, underlength, and path-like identifiers.
- The full regression suite must pass.
- Manual verification uses two independent browser sessions and confirms that data created in either one never appears in the other.
