from rest_framework import serializers
from .models import User , Profile

from django.db import transaction
from django.contrib.auth import authenticate


from rest_framework import serializers
from django.db import transaction
from .models import User, Profile
from django.db import transaction
from django.contrib.auth import get_user_model
from chat.models import Conversation, ConversationMember


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    class Meta:
        model     = Profile
        fields    = ['id','user' , 'username' ,'phone' , 'first_name' , 'last_name' , 'avatar', 'role' , 'created_at' , 'updated_at']
        read_only_fields = ['id' , 'user' , 'username' ,'role' ,'created_at' , 'updated_at']

    def get_role(self, obj):
        return obj.user.role  

    def get_username(self, instance):  
        return instance.user.username


class UserSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    avatar = serializers.ImageField(write_only=True, required=False)
    password = serializers.CharField(write_only=True)

    Profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "role",
            "password",
            "phone",
            "first_name",
            "Profile",
            "last_name",
            "avatar",
        ]
        read_only_fields = ["id" , "Profile"]

    def validate_phone(self, value):
        if not value.startswith("09"):
            raise serializers.ValidationError("شماره موبایل باید با 09 شروع شود")

        if len(value) != 11:
            raise serializers.ValidationError("شماره موبایل باید 11 رقم باشد")

        if not value.isdigit():
            raise serializers.ValidationError("شماره موبایل فقط باید شامل عدد باشد")

        if Profile.objects.filter(phone=value).exists():
            raise serializers.ValidationError("این شماره موبایل قبلاً ثبت شده است")

        return value

    def validate(self, attrs):
        if len(attrs.get("password", "")) < 6:
            raise serializers.ValidationError({
                "password": "رمز عبور باید حداقل 6 کاراکتر باشد"
            })
        return attrs

    @transaction.atomic
    def create(self, validated_data):

        phone = validated_data.pop("phone")
        first_name = validated_data.pop("first_name")
        last_name = validated_data.pop("last_name")
        avatar = validated_data.pop("avatar", None)
        password = validated_data.pop("password")

        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        Profile.objects.create(
            user=user,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            avatar=avatar,
        )

        # ==========================
        # create direct chats
        # ==========================

        other_users = User.objects.exclude(id=user.id)

        for other_user in other_users:

            conversation = Conversation.objects.create(
                type="direct",
                created_by=user
            )

            ConversationMember.objects.create(
                conversation=conversation,
                user=user
            )

            ConversationMember.objects.create(
                conversation=conversation,
                user=other_user
            )

        return user


class CustomAuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)

            if not user:
                raise serializers.ValidationError(
                    "نام کاربری یا رمز عبور اشتباه است.",
                    code="authorization"
                )
        else:
            raise serializers.ValidationError(
                "وارد کردن نام کاربری و رمز عبور الزامی است.",
                code="authorization"
            )


        attrs['user'] = user
        return attrs



    