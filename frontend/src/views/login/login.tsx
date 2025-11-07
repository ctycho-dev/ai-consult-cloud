import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom";
import { Link } from "react-router-dom";
import { Toaster, toast } from 'sonner'
import { useAuth } from "../../components/authProvider";
import { useLoginUserMutation } from "../../api/user";
import { Loader } from '@mantine/core';
import PrimaryButton from "@/components/ui/primaryButton";

const Login = () => {
    const { user } = useAuth();
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [isDisabled, setButtonDisabled] = useState(false)
    const [loginUser, { error }] = useLoginUserMutation() // Destructure the error

    const navigate = useNavigate();

    useEffect(() => {
        if (user) {
            navigate('/')
        }
    }, [user])

    useEffect(() => {
        if (error) {
            // Type guard to check if this is a FetchBaseQueryError
            if ('status' in error) {
                if (error.status === 403) {
                    toast.error('Wrong credentials')
                } else if (error.status === 429) {
                    toast.error('Slow down')
                } else if (error.status === 500) {
                    toast.error('Something went wrong')
                } else {
                    toast.error('Login failed')
                }
            } else {
                // Handle other types of errors (like SerializedError)
                toast.error('Login failed')
            }
        }
    }, [error])

    const handleSubmit = async (e: any) => {
        e.preventDefault()
        setButtonDisabled(true)

        try {
            const res = await loginUser({ email, password })
            if (res && 'data' in res && res.data?.access_token) {
                setEmail('')
                setPassword('')
                navigate('/')
            }
        } catch (err) {
            // This catch block might not be needed since RTK Query handles errors
            toast.error('Something went wrong')
        } finally {
            setButtonDisabled(false)
        }
    }

    return (
        <>
            <div className="w-screen h-screen flex items-center justify-center">
                <div className="px-6 py-12 lg:px-8">
                    <div className="w-[500px]">
                        <h2 className="mt-10 text-center text-2xl/9 font-bold tracking-tight text-gray-900">
                            Войдите в свой аккаунт
                        </h2>
                    </div>

                    <div className="mt-10 w-[500px]">
                        <form action="#" method="POST" className="space-y-6" onSubmit={handleSubmit}>
                            <div>
                                <label htmlFor="email" className="block text-sm/6 font-medium text-gray-900">
                                    Почта
                                </label>
                                <div className="mt-2">
                                    <input
                                        id="email"
                                        name="email"
                                        type="email"
                                        required
                                        autoComplete="email"
                                        value={email}
                                        onChange={(e) => { setEmail(e.target.value) }}
                                        className="block w-full rounded-lg bg-white px-3 py-1.5 text-base text-gray-900 outline outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-primary_green sm:text-sm/6"
                                    />
                                </div>
                            </div>

                            <div>
                                <div className="flex items-center justify-between">
                                    <label htmlFor="password" className="block text-sm/6 font-medium text-gray-900">
                                        Пароль
                                    </label>
                                    {/* <div className="text-sm">
                                        <a href="#" className="font-semibold text-ia-text-interactive">
                                            Забыли пароль?
                                        </a>
                                    </div> */}
                                </div>
                                <div className="mt-2">
                                    <input
                                        id="password"
                                        name="password"
                                        type="password"
                                        required
                                        autoComplete="current-password"
                                        value={password}
                                        onChange={(e) => { setPassword(e.target.value) }}
                                        className="block w-full rounded-lg bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-primary_green sm:text-sm/6"
                                    />
                                </div>
                            </div>

                            <div>
                                <PrimaryButton type="submit" className="w-full" disabled={isDisabled}>
                                    {isDisabled ? <Loader size="sm" /> : 'Войти'}
                                </PrimaryButton>
                            </div>
                        </form>

                        {/* <p className="mt-10 text-center text-sm/6 text-gray-500">
                            Не зарегестрированы?{' '}
                            <Link to={'/signup'} className="font-semibold text-ia-text-interactive">
                                Обратитесь к администратору
                            </Link>
                        </p> */}
                    </div>
                </div>
            </div>
            <Toaster richColors position="top-right" />
        </>
    )
}

export default Login