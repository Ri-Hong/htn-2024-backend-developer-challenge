### We don't store the the skills and ratings as an array in the participants table in order to preserve normalization. Normalization aims to reduce redundancy and improve data integrity by ensuring that each piece of data is stored only once.

Working with denormalized data can cause these issues:

1. uery Complexity: Searching, filtering, or joining data based on values within an array can be more complex and less efficient than with normalized data.
2. Data Integrity: Ensuring the integrity of data within an array (e.g., no duplicates, valid values) is more challenging.
3. Updates and Scalability: Modifying a single element within an array requires reading and rewriting the entire array, which can be inefficient. As the data grows, these operations can become increasingly cumbersome and slow.

### We have a seperate table for Skills and a seperate junction table for the many to many relationship between participants and skills.

We don't store the skills directly in the participants table because:

1. Avoiding Redundancy: Storing skill names directly in the ParticipantSkills table would lead to redundancy. The same skill name would be repeated for each participant possessing that skill, consuming more storage and potentially leading to inconsistencies (e.g., spelling errors leading to the same skill being listed under multiple variations).
2. Data Integrity and Consistency: A separate Skills table ensures that each skill is defined once and only once, maintaining a single source of truth. This approach prevents inconsistencies in skill names and makes it easier to update or correct a skill name across all associations.
3. Efficiency: Linking participants to skills through IDs is more efficient than using text strings. Integer comparisons (IDs) are faster than string comparisons (skill names), which can improve the performance of queries, especially as the dataset grows.
4. Flexibility for Future Changes: If you need to add more information about a skill (e.g., a description, category, or proficiency level required), having a separate Skills table makes it easier to extend the database schema without affecting the structure of other tables.
5. Simplifying Relationships: By using a ParticipantSkills junction table, you can easily manage many-to-many relationships between participants and skills, including storing additional information about each association, such as the rating, without complicating the schema.

### Use a Many-to-Many Relationship

The many-to-many relationship between participants and skills is modeled using a junction table called ParticipantSkills. This table contains two foreign keys, participant_id and skill_id, which reference the primary keys of the participants and skills tables, respectively. The combination of these two foreign keys forms a composite primary key for the ParticipantSkills table, ensuring that each participant-skill association is unique.

## Assumptions:

Some data had some strange entries, so the following assumptions were made and the data was cleaned accordingly:

1. Emails and phone numbers must be unique. If we try to insert a participant with an email or phone number that already exists, we will skip that participant and log a warning message.

2. Each user cannot have the same skill with multiple ratings. If we try to insert the a skill that already has a rating under the same user, we will skip that skill and log a warning message.

db_init.py will output warning messages if any of the above assumptions are violated.

```json
{
  "skills": [
    {
      "skill": "Swift",
      "rating": 70
    },
    {
      "skill": "Swift",
      "rating": 80
    }
  ]
}
```

If we call `PUT /users/{user_id}` with the above JSON, we will skip the second skill and the skill will be updated to 70.
