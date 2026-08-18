create table public.meal_estimates (
    id uuid primary key,
    user_id uuid not null default auth.uid() references auth.users (id) on delete cascade,
    observed_at timestamptz not null default now(),
    meal_name text not null check (char_length(meal_name) between 1 and 160),
    calories numeric(8, 2) not null check (calories between 0 and 10000),
    protein_g numeric(8, 2) not null check (protein_g between 0 and 1000),
    carbs_g numeric(8, 2) not null check (carbs_g between 0 and 2000),
    fat_g numeric(8, 2) not null check (fat_g between 0 and 1000),
    identity_confidence numeric(4, 3) not null check (identity_confidence between 0 and 1),
    portion_confidence numeric(4, 3) not null check (portion_confidence between 0 and 1),
    nutrition_confidence numeric(4, 3) not null check (nutrition_confidence between 0 and 1),
    foods jsonb not null default '[]'::jsonb check (jsonb_typeof(foods) = 'array'),
    assumptions jsonb not null default '[]'::jsonb check (jsonb_typeof(assumptions) = 'array'),
    source_summary text not null check (char_length(source_summary) between 1 and 500),
    user_note text check (user_note is null or char_length(user_note) <= 500),
    model_name text not null check (char_length(model_name) between 1 and 120),
    user_confirmed boolean not null default true,
    created_at timestamptz not null default now()
);

create index meal_estimates_user_observed_at_idx
    on public.meal_estimates (user_id, observed_at desc);

alter table public.meal_estimates enable row level security;

revoke all on table public.meal_estimates from anon;
grant select, insert, update, delete on table public.meal_estimates to authenticated;
grant all on table public.meal_estimates to service_role;

create policy "Users can read their own meal estimates"
on public.meal_estimates
for select
to authenticated
using ((select auth.uid()) = user_id);

create policy "Users can insert their own meal estimates"
on public.meal_estimates
for insert
to authenticated
with check ((select auth.uid()) = user_id);

create policy "Users can update their own meal estimates"
on public.meal_estimates
for update
to authenticated
using ((select auth.uid()) = user_id)
with check ((select auth.uid()) = user_id);

create policy "Users can delete their own meal estimates"
on public.meal_estimates
for delete
to authenticated
using ((select auth.uid()) = user_id);
