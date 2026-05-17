from skills.linkedin_skill import LinkedInSkill

skill = LinkedInSkill()
print("Starting LinkedIn Comment Test...")
result = skill.post_reply("Details", "Thank you for engaging with K-Electric! ⚡")
print(f"Result: {result}")
