# from django import forms


# class ContactForm(forms.Form):
#     name = forms.CharField(
#         max_length=100,
#         label="Your Name",
#         widget=forms.TextInput(
#             attrs={
#                 "placeholder": "Your name",
#                 "class": "pk-contact-input",
#             }
#         ),
#     )

#     email = forms.EmailField(
#         label="Email Address",
#         widget=forms.EmailInput(
#             attrs={
#                 "placeholder": "Your email address",
#                 "class": "pk-contact-input",
#             }
#         ),
#     )

#     phone = forms.CharField(
#         max_length=20,
#         required=False,
#         label="Phone Number",
#         widget=forms.TextInput(
#             attrs={
#                 "placeholder": "Your phone number",
#                 "class": "pk-contact-input",
#             }
#         ),
#     )

#     message = forms.CharField(
#         label="Message",
#         widget=forms.Textarea(
#             attrs={
#                 "placeholder": "How can we help you?",
#                 "class": "pk-contact-input pk-contact-textarea",
#                 "rows": 6,
#             }
#         ),
#     )
