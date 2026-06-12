create extension if not exists pgcrypto;

create table interviews (
  id uuid primary key default gen_random_uuid(),
  status text not null default 'DRAFT',
  title text,
  target_questions int default 8,
  current_question_number int default 0,
  current_difficulty numeric default 5,
  match_analysis_json jsonb,
  report_json jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now(),

  constraint interviews_status_check
    check (status in ('DRAFT', 'READY', 'IN_PROGRESS', 'COMPLETED', 'FAILED')),

  constraint interviews_target_questions_check
    check (target_questions > 0),

  constraint interviews_difficulty_check
    check (current_difficulty >= 3 and current_difficulty <= 10)
);

create table messages (
  id uuid primary key default gen_random_uuid(),
  interview_id uuid references interviews(id) on delete cascade,
  role text not null,
  content text not null,
  question_number int,
  difficulty_level numeric,
  answer_quality_score numeric,
  response_time_ms int,
  paste_detected boolean default false,
  created_at timestamptz default now(),

  constraint messages_role_check
    check (role in ('assistant', 'candidate', 'system')),

  constraint messages_score_check
    check (answer_quality_score is null or (answer_quality_score >= 0 and answer_quality_score <= 10))
);

create index idx_messages_interview_id
  on messages(interview_id);

create index idx_messages_interview_question
  on messages(interview_id, question_number);

create or replace function update_updated_at_column()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger update_interviews_updated_at
before update on interviews
for each row
execute function update_updated_at_column();