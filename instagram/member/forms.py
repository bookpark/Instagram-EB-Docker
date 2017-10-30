from django import forms
from django.contrib.auth import get_user_model, login, authenticate
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class SignupForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        class_update_fields = ('password1', 'password2')
        for field in class_update_fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
            })

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'username',
            'nickname',
            'password1',
            'password2',
            'img_profile',
            'age',
        )
        widgets = {
            'username': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'nickname': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'age': forms.NumberInput(
                attrs={
                    'class': 'form-control'
                }
            ),
        }

        # class SignupForm(forms.Form):
        #     username = forms.CharField(
        #         widget=forms.TextInput(
        #             attrs={
        #                 'class': 'form-control',
        #             }
        #         )
        #     )
        #     age = forms.IntegerField(
        #         widget=forms.NumberInput(
        #             attrs={
        #                 'class': 'form-control',
        #             }
        #         )
        #     )
        #     password = forms.CharField(
        #         widget=forms.PasswordInput(
        #             attrs={
        #                 'class': 'form-control',
        #             }
        #         )
        #     )
        #
        #     password2 = forms.CharField(
        #         widget=forms.PasswordInput(
        #             attrs={
        #                 'class': 'form-control',
        #             }
        #         )
        #     )
        #
        #     # clean_<field_name>
        #     def clean_username(self):
        #         data = self.cleaned_data['username']
        #         if User.objects.filter(username=data).exists():
        #             raise forms.ValidationError(f'Username {data} already exists.')
        #         return data
        #
        #     def clean_password2(self):
        #         password = self.cleaned_data['password']
        #         password2 = self.cleaned_data['password2']
        #         if password != password2:
        #             raise forms.ValidationError('Password does not match.')
        #         return password2
        #
        #     def clean(self):
        #         if self.is_valid():
        #             setattr(self, 'signup', self._signup)
        #         return self.cleaned_data
        #
        #     def _signup(self):
        #         username = self.cleaned_data['username']
        #         password = self.cleaned_data['password']
        #         age = self.cleaned_data['age']
        #         return User.objects.create_user(
        #             username=username,
        #             password=password,
        #             age=age,
        #         )


class SigninForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
            }
        )
    )

    # 초기화 함수 __init__, self.user 사용 위해 정의
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        self.user = authenticate(
            username=username,
            password=password,
        )
        if not self.user:
            raise forms.ValidationError('Login failed')
        else:
            # 동적으로 작동
            setattr(self, 'signin', self._signin)

    def _signin(self, request):
        """

        :param request: django.auth.login()에 주어질 HttpRequest 객체
        :return:
        """
        if self.user:
            login(request, self.user)
