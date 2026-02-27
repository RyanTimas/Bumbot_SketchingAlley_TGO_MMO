select * from tgommo_creature c;
select * from tgommo_environment e;
select * from tgommo_environment_creature ec;
select * from tgommo_user_creature tuc;

select * from users;
select * from user_avatar ua;
select * from tgommo_user_profile_avatar_link ual;
select * from tgommo_user_avatar_unlock_condition uauc;
---------------------------------------------------------------------------------------------------------
Delete from tgommo_user_profile_avatar_link WHERE avatar_id   = 'E13';


    SELECT 
        DISTINCT(uc.catch_id), c.creature_id, 
        c.name, c.variant_name, ec.local_name, uc.nickname, 
        c.dex_no, c.variant_no, ec.local_dex_no, ec.local_variant_no,
        c.full_name, c.scientific_name, c.kingdom, c.description, 
        c.img_root, ec.local_img_root,
        ec.sub_environment_type, 
        c.encounter_rate, 
        c.default_rarity, ec.spawn_rarity, uc.is_mythical, 
        uc.catch_date, uc.is_favorite, uc.is_released 
    FROM tgommo_user_creature uc 
        LEFT JOIN tgommo_environment_creature ec ON uc.creature_id = ec.creature_id AND uc.environment_id = ec.environment_id 
        LEFT JOIN tgommo_creature c ON c.creature_id = ec.creature_id 
    WHERE 
 uc.user_id = 801108873955115028 AND uc.is_released = 0;








---------------------------------------------------------------------------------------------------------
DROP TABLE tgommo_creature;
DROP TABLE tgommo_environment;
DROP TABLE tgommo_environment_creature;
DROP TABLE tgommo_user_creature;

DROP TABLE user_avatar;
DROP TABLE tgommo_user_profile_avatar_link;
DROP TABLE tgommo_user_avatar_unlock_condition;


