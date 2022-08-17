import { Container, Input, Title, Main, Form, Button } from '../../components'
import styles from './styles.module.css'
import { useFormWithValidation } from '../../utils'
import { AuthContext } from '../../contexts'
import { Redirect } from 'react-router-dom'
import { useContext } from 'react'
import MetaTags from 'react-meta-tags'

const ChangePassword = ({ onPasswordChange }) => {
  const { values, handleChange, errors, isValid, resetForm } = useFormWithValidation()
  const authContext = useContext(AuthContext)

  return <Main>
    <Container>
      <MetaTags>
        <title>Change the password</title>
        <meta name="description" content="Foodgram - Change the password" />
        <meta property="og:title" content="Change the password" />
      </MetaTags>
      <Title title='Change the password' />
      <Form
        className={styles.form}
        onSubmit={e => {
          e.preventDefault()
          onPasswordChange(values)
        }}
      >
        <Input
          required
          label='Old password'
          type='password'
          name='current_password'
          onChange={handleChange}
        />
        <Input
          required
          label='New passowrd'
          type='password'
          name='new_password'
          onChange={handleChange}
        />
        <Input
          required
          label='Confirmation of new password'
          type='password'
          name='repeat_password'
          onChange={handleChange}
        />
        <Button
          modifier='style_dark-blue'
          type='submit'
          disabled={!isValid || values.new_password !== values.repeat_password}
        >
          Change the passowrd
        </Button>
      </Form>
    </Container>
  </Main>
}

export default ChangePassword
