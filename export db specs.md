there are a few things to export:

1. participants
2. participant payments
3. ambassadors
4. program analytics

note:
    - program_id is required for all exports
    - unless required, all optional so send all data of that filter if not specified

here are the details and where to get the data from:

1. participants
    tables: users, participants, participant_essays, participant_statuses, participant_subthemes, payments, program_payments, program_essays, program_subthemes, programs, participant_competition_categories, competition_categories

    filters are:
        - program_id (required)
        - category - self_funded, fully_funded
        - form_status - not started, in_progress, submitted
        - payment_done - array of program payment ids; any program payment id in this array means payment successful
        - with_essay - boolean
        - created_at - date range

    - email is from users table
    - for phone number, include country code and phone number from participants table
    - form_status is from participant_statuses table: not started = 0, in_progress = 1, submitted = 2
    - payment_done is from payments table; join payments on participants.id = payments.participant_id and payments.program_payment_id in (array) and check payments.status = '2' (successful)
    - category is from participants table; enum of self_funded, fully_funded
    - with_essay = true means participant_essays.participant_id is not null or empty, get essay questions from program_essays table and join participant_essays on participant_essays.program_essay_id = program_essays.id
    - subthemes = join participant_subthemes on participant_subthemes.participant_id = participants.id and join program_subthemes on participant_subthemes.program_subtheme_id = program_subthemes.id
    - competition categories = join participant_competition_categories on participant_competition_categories.participant_id = participants.id and join competition_categories on participant_competition_categories.competition_category_id = competition_categories.id
    - created_at is from participants.created_at
