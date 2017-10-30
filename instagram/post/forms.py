from django import forms

from .models import Post, Comment

__all__ = (
    'PostForm',
    'CommentForm',
)


class PostForm(forms.ModelForm):
    # 아래 코드는 Meta에 필드가 지정이 되어 있을 때 override 하는 경우 쓰인다
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['author'].required = True

    class Meta:
        model = Post
        # fields = '__all__'
        fields = (
            'photo',
        )

    def save(self, commit=True, *args, **kwargs):
        # 새로 저장하려는 객체이며(pk값이 없음), DB에 바로 저장하려고 할 경우(commit=True)
        if not self.instance.pk and commit:
            # author 값을 키워드 인수 묶음에서 pop으로 삭제하며 가져온다
            author = kwargs.pop('author', None)
            # author 값이 없을 경우 (키워드가 없었거나 값이 주어지지 않거나)
            if not author:
                # ValueError를 발생시킴
                raise ValueError('Author field is required')
            # author 값이 존재하면 자신의 instance의 author 필드 값을 채움
            self.instance.author = author
        # super 클래스의 save 호출
        return super().save(*args, **kwargs)

        # if not self.instance.pk and commit:
        #     raise ValueError('PostForm commit=True(save) is not allowed')
        # return super().save(*args, **kwargs)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = (
            'content',
        )
        widgets = {
            'content': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            )
        }
