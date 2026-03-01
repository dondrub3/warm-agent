#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件服务模块
用于发送API key和通知邮件
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional


class EmailService:
    """邮件服务"""
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@warmagent.ai")
        self.enabled = all([self.smtp_host, self.smtp_user, self.smtp_password])
    
    def _send_email(self, to_email: str, subject: str, html_content: str, text_content: str) -> bool:
        """发送邮件"""
        if not self.enabled:
            print(f"Email service not configured. Would send to {to_email}:")
            print(f"Subject: {subject}")
            print(f"Content: {text_content}")
            return True
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # 添加纯文本和HTML版本
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # 发送邮件
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, to_email, msg.as_string())
            
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    def send_api_key(self, to_email: str, api_key: str, plan: str = "free") -> bool:
        """发送API key邮件"""
        subject = "🎉 欢迎使用 Warm Agent - 您的 API Key"
        
        quota_limit = {"free": 1000, "pro": 10000, "enterprise": 100000}.get(plan, 1000)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .api-key {{ background: #2d3748; color: #68d391; padding: 15px; border-radius: 5px; font-family: monospace; font-size: 14px; word-break: break-all; margin: 20px 0; }}
                .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 30px; }}
                .highlight {{ color: #667eea; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 欢迎使用 Warm Agent</h1>
                    <p>为您的 AI 注入温度与情感</p>
                </div>
                <div class="content">
                    <h2>您好！</h2>
                    <p>感谢您注册 Warm Agent。您的 API Key 已生成，请妥善保管：</p>
                    
                    <div class="api-key">{api_key}</div>
                    
                    <p><strong>套餐类型：</strong> <span class="highlight">{plan.upper()}</span></p>
                    <p><strong>每月额度：</strong> <span class="highlight">{quota_limit:,}</span> 次请求</p>
                    
                    <h3>🚀 快速开始</h3>
                    <ol>
                        <li>复制上方的 API Key</li>
                        <li>在请求头中添加：<code>X-API-Key: {api_key}</code></li>
                        <li>调用 API 获取情感分析服务</li>
                    </ol>
                    
                    <center>
                        <a href="http://localhost:8000/docs" class="button">查看 API 文档</a>
                    </center>
                    
                    <h3>📊 查看用量</h3>
                    <p>访问 Dashboard 查看实时用量统计：<br>
                    <a href="http://localhost:8000/dashboard">http://localhost:8000/dashboard</a></p>
                    
                    <p><strong>注意：</strong> 请勿与他人分享您的 API Key。如需重置，请登录 Dashboard 重新生成。</p>
                    
                    <div class="footer">
                        <p>Warm Agent Team</p>
                        <p>如有问题，请联系 support@warmagent.ai</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
欢迎使用 Warm Agent!

您的 API Key: {api_key}
套餐类型: {plan.upper()}
每月额度: {quota_limit:,} 次请求

快速开始:
1. 在请求头中添加: X-API-Key: {api_key}
2. 调用 API 获取情感分析服务
3. 查看文档: http://localhost:8000/docs

查看用量: http://localhost:8000/dashboard

如有问题，请联系 support@warmagent.ai
"""
        
        return self._send_email(to_email, subject, html_content, text_content)
    
    def send_quota_warning(self, to_email: str, quota_used: int, quota_limit: int) -> bool:
        """发送额度警告邮件"""
        usage_percent = quota_used / quota_limit * 100
        
        subject = "⚠️ Warm Agent 用量提醒"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 20px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>⚠️ 用量提醒</h2>
                <div class="warning">
                    <p>您的 API 用量已使用 <strong>{usage_percent:.1f}%</strong></p>
                    <p>已用: {quota_used:,} / 总额: {quota_limit:,}</p>
                </div>
                <p>如需更多额度，请考虑升级到 Pro 套餐。</p>
                <p><a href="http://localhost:8000/dashboard">查看 Dashboard</a></p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
用量提醒

您的 API 用量已使用 {usage_percent:.1f}%
已用: {quota_used:,} / 总额: {quota_limit:,}

如需更多额度，请考虑升级到 Pro 套餐。
查看 Dashboard: http://localhost:8000/dashboard
"""
        
        return self._send_email(to_email, subject, html_content, text_content)


# 全局邮件服务实例
_email_service = None

def get_email_service() -> EmailService:
    """获取邮件服务实例（单例）"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
