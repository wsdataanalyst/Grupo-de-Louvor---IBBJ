"""Sincroniza profile_photo no CSV com arquivo em disco (evita import circular com app)."""

from __future__ import annotations

import pandas as pd


def sync_user_profile_photo_field(members_df: pd.DataFrame) -> pd.DataFrame:
    """Alinha profile_photo no members.csv com a foto salva em profile_photos/."""
    import streamlit as st

    from app import MEMBERS_FILE, get_current_member_row, profile_photo_file, save_data

    idx, row = get_current_member_row(members_df)
    if idx is None or row is None:
        return members_df
    email = str(row["email"]).strip().lower()
    stored = str(row.get("profile_photo", "")).strip()
    path = profile_photo_file(email, stored)
    if not path:
        return members_df
    fn = path.name
    if stored != fn:
        members_df = members_df.copy()
        members_df.at[idx, "profile_photo"] = fn
        if save_data(members_df, MEMBERS_FILE, quiet=True):
            st.session_state.user_profile_photo = fn
    else:
        st.session_state.user_profile_photo = stored or fn
    return members_df
